import httpx
import random
import logging
import asyncio
import time
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

from utils.hash_util import generate_hash
from core.sources import URLS
from core.config import SSL_VERIFY_EXEMPT, TARGET_YEARS, REQUEST_TIMEOUT
from scraper.date_extractor import extract_date
from scraper.pdf_processor import get_date_from_pdf

logger = logging.getLogger("SCRAPER")

# Robust User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/121.0.0.0 Safari/537.36"
]

# CIRCUIT BREAKER STATE
source_health = {}
MAX_FAILURES = 3
COOLDOWN_SECONDS = 1800  # 30 Minutes


def _parse_html_sync(html_content, source_config):
    """
    CPU-BOUND TASK: Universal Link Extractor with Deep Sibling Scanning.
    Walks through MULTIPLE siblings to find contextual text and prevent cross-contamination.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    items = []
    
    def get_contextual_text(a_tag, max_siblings=10, max_chars=150):
        """
        Walks backwards through siblings to collect surrounding text.
        Stops after max_siblings or max_chars reached.
        
        Args:
            a_tag: BeautifulSoup anchor tag
            max_siblings: Maximum number of siblings to check
            max_chars: Maximum characters to collect
            
        Returns:
            Combined text from siblings + link text
        """
        text_parts = []
        char_count = 0
        current = a_tag.previous_sibling
        sibling_count = 0
        
        # Walk BACKWARDS through previous siblings
        while current and sibling_count < max_siblings and char_count < max_chars:
            # Check if this is an HTML tag (has a 'name' attribute)
            if hasattr(current, 'name') and current.name:
                # It's an HTML tag (like <br>, <a>, <span>), skip to next sibling
                current = current.previous_sibling
                sibling_count += 1
                continue
            
            # It's a text node (NavigableString)
            text = str(current).strip()
            
            # Only collect meaningful text (not empty, not too large)
            if text and len(text) < 100:
                text_parts.insert(0, text)  # Insert at beginning to maintain order
                char_count += len(text)
            
            current = current.previous_sibling
            sibling_count += 1
        
        # Add the link's own text at the end
        link_text = a_tag.get_text(" ", strip=True)
        text_parts.append(link_text)
        
        return " ".join(text_parts).strip()
    
    # Process all anchor tags
    for a in soup.find_all("a", href=True):
        full_url = urljoin(source_config["url"], a["href"])
        
        # STRATEGY 1: Try isolated parent first (single-link containers like <li>)
        if a.parent and len(a.parent.find_all("a")) == 1:
            # This link is alone in its parent - safe to use parent text
            parent_text = a.parent.get_text(" ", strip=True)
            
            if parent_text and len(parent_text) < 300:
                # Parent text is reasonable size - use it
                final_text = parent_text
            else:
                # Parent too large (might be a nested container), use sibling walker
                final_text = get_contextual_text(a)
        else:
            # STRATEGY 2: Multi-link container - use deep sibling scan to avoid contamination
            final_text = get_contextual_text(a)
        
        items.append({
            "text": final_text,
            "url": full_url
        })
            
    return items


async def build_item(raw_data, source_name):
    """
    Async Processor for individual items.
    Validates and enriches raw scraped data.
    """
    title = raw_data["text"]
    url = raw_data["url"]

    if not title or not url: 
        return None
    
    # 1. Forensic Noise Filtering
    BLOCKLIST = [
        "about us", "contact", "home", "back", "gallery", 
        "archive", "click here", "apply now", "visit", "syllabus"
    ]
    
    if len(title) < 5 or any(k in title.lower() for k in BLOCKLIST): 
        return None

    # 2. Date Discovery (Title with context from siblings)
    real_date = extract_date(title) 
    
    # 🔧 OPTIONAL: Fallback to PDF date if HTML date not found
    if not real_date and url and ".pdf" in url.lower():
        logger.debug(f"🔍 No HTML date, checking PDF metadata for: {title[:50]}...")
        real_date = await get_date_from_pdf(url)
    
    # 🚨 ABSOLUTE SHIELD: No Date? DROP IT.
    if not real_date:
        # TEMPORARY DEBUG: Log which notices are being dropped
        logger.debug(f"⚠️ NO DATE FOUND - Dropped: {title[:60]}...")
        return None

    # 3. Refined GHOST FILTER (Old academic year references)
    OLD_YEARS = ["2019", "2020", "2021", "2022", "2023"]
    if any(y in title for y in OLD_YEARS):
        # If extracted date is old, DROP IT.
        if str(real_date.year) in OLD_YEARS:
            logger.debug(f"⚠️ OLD YEAR - Dropped: {title[:60]}...")
            return None

    # 4. Validity Check (Dynamic Year Window)
    if real_date and real_date.year in TARGET_YEARS:
        return {
            "title": title.strip(),
            "source": source_name,
            "source_url": url,
            "pdf_url": url if ".pdf" in url.lower() else None,
            "content_hash": generate_hash(title, url),
            "published_date": real_date,
            "scraped_at": datetime.utcnow()
        }
    
    return None


async def scrape_source(source_key, source_config):
    """
    Main scraping function with circuit breaker and error handling.
    """
    # --- CIRCUIT BREAKER CHECK ---
    health = source_health.get(source_key, {"fails": 0, "next_try": 0})
    if time.time() < health["next_try"]:
        return []

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    verify = not any(domain in source_config["url"] for domain in SSL_VERIFY_EXEMPT)
    
    try:
        # Random delay to avoid detection
        await asyncio.sleep(random.uniform(2, 5)) 
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, verify=verify, follow_redirects=True) as client:
            r = await client.get(source_config["url"], headers=headers)
            r.raise_for_status()

            # Offload CPU-intensive parsing to thread pool
            raw_items = await asyncio.to_thread(_parse_html_sync, r.text, source_config)
            
            logger.info(f"🔎 {source_key}: Analyzing {len(raw_items)} candidates...")
            
            valid_items = []
            for raw in raw_items:
                item = await build_item(raw, source_config["source"])
                if item: 
                    valid_items.append(item)

            # Reset failure counter on success
            source_health[source_key] = {"fails": 0, "next_try": 0}
            
            if valid_items:
                logger.info(f"✅ {source_key}: Extracted {len(valid_items)} valid notices.")
            else:
                logger.warning(f"⚠️ {source_key}: No valid items after filtering.")
                
            return valid_items

    except Exception as e:
        fails = health["fails"] + 1
        wait_time = 0
        
        if fails >= MAX_FAILURES:
            wait_time = COOLDOWN_SECONDS
            logger.error(f"❌ {source_key} BROKEN: {e}. Cooling down for {wait_time}s.")
        else:
            logger.warning(f"⚠️ {source_key} Glitch: {e}")
        
        source_health[source_key] = {
            "fails": fails, 
            "next_try": time.time() + wait_time
        }
        return []

#@academictelebotbyroshhellwett
