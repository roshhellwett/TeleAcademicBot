import io
import pdfplumber
import requests
import logging
from scraper.date_extractor import extract_date

logger = logging.getLogger("PDF_PROCESSOR")

def get_date_from_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, timeout=20, verify=False, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            if not pdf.pages:
                return None
                
            first_page = pdf.pages[0]
            width, height = first_page.width, first_page.height
            
            # 🎯 STRIKE ZONE: Absolute Top-Right corner only.
            # This avoids picking up dates from the middle of the text.
            header_box = (width * 0.55, 0, width, height * 0.20)
            header_area = first_page.within_bbox(header_box)
            header_text = header_area.extract_text()
            
            # Try extraction from the tiny top-right box first
            date = extract_date(header_text)
            if date:
                logger.info(f"✅ Header Date Found: {date.date()}")
                return date

            # FALLBACK: If top-right fails, check for "Dated:" anywhere in the top 30%
            full_header_box = (0, 0, width, height * 0.30)
            full_header_text = first_page.within_bbox(full_header_box).extract_text()
            return extract_date(full_header_text)
            
    except Exception as e:
        logger.warning(f"PDF Error: {e}")
        return None