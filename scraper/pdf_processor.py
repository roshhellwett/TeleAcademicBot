import logging
import pdfplumber
import httpx
import io
import asyncio
import random
from datetime import datetime
from scraper.date_extractor import extract_date
from core.config import SSL_VERIFY_EXEMPT, REQUEST_TIMEOUT, MAX_PDF_SIZE_MB

logger = logging.getLogger("PDF_PROC")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def _parse_pdf_sync(pdf_bytes):
    """CPU-bound parsing (Sync)."""
    try:
        with pdfplumber.open(pdf_bytes) as pdf:
            if not pdf.pages: return None
            
            # 1. Metadata Scan
            meta = pdf.metadata.get('CreationDate')
            if meta:
                clean = meta.replace("D:", "")[:8]
                return datetime.strptime(clean, "%Y%m%d")

            # 2. Text Scan (Page 1)
            text = pdf.pages[0].extract_text()
            return extract_date(text)
    except Exception:
        return None

async def get_date_from_pdf(pdf_url):
    """Memory-Safe PDF Fetcher."""
    verify = not any(d in pdf_url for d in SSL_VERIFY_EXEMPT)
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        async with httpx.AsyncClient(verify=verify, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            # 1. HEAD Request (Check size before downloading)
            head_resp = await client.head(pdf_url, headers=headers)
            size = int(head_resp.headers.get("Content-Length", 0))
            
            if size > (MAX_PDF_SIZE_MB * 1024 * 1024):
                logger.warning(f"⚠️ PDF Too Large ({size} bytes): {pdf_url}")
                return None

            # 2. Download (Streamed)
            resp = await client.get(pdf_url, headers=headers)
            if resp.status_code != 200: return None

            pdf_bytes = io.BytesIO(resp.content)
            
            # 3. Offload Parsing
            return await asyncio.to_thread(_parse_pdf_sync, pdf_bytes)

    except Exception as e:
        logger.warning(f"⚠️ PDF Fail: {e}")
        return None
        #@academictelebotbyroshhellwett