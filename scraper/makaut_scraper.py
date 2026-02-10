import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger("SCRAPER")

MAKAUT_MAIN = "https://makautwb.ac.in/page.php?id=340"
MAKAUT_EXAM = "https://makautexam.net"


# ===== SESSION (FASTER NETWORK) =====
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "TeleAcademicBot/1.0"
})


# ===== HASH =====
def _hash(title, url):
    return hashlib.sha256(f"{title}{url}".encode()).hexdigest()


# ===== SAFE VALIDATION =====
def safe_item(item):
    if not item.get("title"):
        return None
    if not item.get("source_url"):
        return None
    return item


# ===== MAIN SITE PARSER =====
def _parse_makaut_main():

    data = []

    try:
        r = SESSION.get(MAKAUT_MAIN, timeout=20)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        seen_hash = set()

        for a in soup.find_all("a"):

            title = a.text.strip()
            href = a.get("href")

            if not title or not href:
                continue

            if not href.startswith("http"):
                href = "https://makautwb.ac.in/" + href.lstrip("/")

            h = _hash(title, href)

            if h in seen_hash:
                continue
            seen_hash.add(h)

            item = {
                "title": title,
                "source": "MAKAUT WB",
                "source_url": href,
                "pdf_url": href if ".pdf" in href.lower() else None,
                "content_hash": h,
                "published_date": datetime.utcnow(),
                "scraped_at": datetime.utcnow()
            }

            item = safe_item(item)
            if item:
                data.append(item)

    except Exception as e:
        logger.error(f"MAIN SCRAPE ERROR {e}")

    return data


# ===== EXAM SITE PARSER =====
def _parse_exam():

    data = []

    try:
        r = SESSION.get(MAKAUT_EXAM, timeout=20)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        seen_hash = set()

        for a in soup.find_all("a"):

            title = a.text.strip()
            href = a.get("href")

            if not title or not href:
                continue

            if not href.startswith("http"):
                href = "https://makautexam.net/" + href.lstrip("/")

            h = _hash(title, href)

            if h in seen_hash:
                continue
            seen_hash.add(h)

            item = {
                "title": title,
                "source": "MAKAUT EXAM",
                "source_url": href,
                "pdf_url": href if ".pdf" in href.lower() else None,
                "content_hash": h,
                "published_date": datetime.utcnow(),
                "scraped_at": datetime.utcnow()
            }

            item = safe_item(item)
            if item:
                data.append(item)

    except Exception as e:
        logger.error(f"EXAM SCRAPE ERROR {e}")

    return data


# ===== MASTER SCRAPER =====
def scrape_all_sources():

    all_data = []

    try:
        main = _parse_makaut_main()
        exam = _parse_exam()

        all_data.extend(main)
        all_data.extend(exam)

        logger.info(f"TOTAL SCRAPED SAFE ITEMS {len(all_data)}")

    except Exception as e:
        logger.error(f"SCRAPE ALL ERROR {e}")

    return all_data
#@roshhellwett makaut tele bot