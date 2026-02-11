import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import logging
import time

from core.sources import URLS

logger = logging.getLogger("SCRAPER")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "TeleAcademicBot/Production"
})


# ===== HASH =====
def generate_hash(title, url):
    return hashlib.sha256(f"{title}{url}".encode()).hexdigest()


# ===== SAFE VALIDATION =====
def build_item(title, url, source_name):

    if not title or not url:
        return None

    return {
        "title": title.strip(),
        "source": source_name,
        "source_url": url,
        "pdf_url": url if ".pdf" in url.lower() else None,
        "content_hash": generate_hash(title, url),
        "published_date": datetime.utcnow(),
        "scraped_at": datetime.utcnow()
    }


# ===== GENERIC PAGE PARSER =====
def parse_generic_links(base_url, source_name):

    data = []
    seen = set()

    try:
        r = SESSION.get(base_url, timeout=25)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a"):

            title = a.text.strip()
            href = a.get("href")

            if not title or not href:
                continue

            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")

            h = generate_hash(title, href)

            if h in seen:
                continue

            seen.add(h)

            item = build_item(title, href, source_name)

            if item:
                data.append(item)

    except Exception as e:
        logger.error(f"{source_name} SCRAPE ERROR {e}")

    return data


# ===== SCRAPE SINGLE SOURCE WITH RETRY =====
def scrape_source(source_key, source_config):

    url = source_config["url"]
    source_name = source_config["source"]

    for attempt in range(3):
        try:
            return parse_generic_links(url, source_name)
        except Exception as e:
            logger.warning(f"{source_key} attempt {attempt+1} failed {e}")
            time.sleep(2)

    logger.error(f"{source_key} FAILED AFTER RETRIES")
    return []


# ===== MASTER SCRAPER =====
def scrape_all_sources():

    all_data = []

    try:
        for key, config in URLS.items():

            logger.info(f"SCRAPING SOURCE {key}")

            source_data = scrape_source(key, config)

            logger.info(f"{key} -> {len(source_data)} items")

            all_data.extend(source_data)

        logger.info(f"TOTAL SCRAPED SAFE ITEMS {len(all_data)}")

    except Exception as e:
        logger.error(f"SCRAPE ALL ERROR {e}")

    return all_data
