import io
import pdfplumber
import requests
import logging
from scraper.date_extractor import extract_date

logger = logging.getLogger("PDF_PROCESSOR")

def get_date_from_pdf(pdf_url):
    """Enhanced PDF reader specifically for MAKAUT scanned headers."""
    try:
        response = requests.get(
            pdf_url, 
            timeout=20, 
            verify=False,
            headers={"User-Agent": "Mozilla/5.0"} 
        )
        
        if response.status_code != 200:
            return None

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            if not pdf.pages:
                return None
                
            first_page = pdf.pages[0]
            width, height = first_page.width, first_page.height
            
            # 1. PRIMARY SEARCH: Top 30% of the page, Right 60% 
            # (Expanded slightly to ensure we catch the 'Date:' line)
            header_box = (width * 0.4, 0, width, height * 0.30)
            header_area = first_page.within_bbox(header_box)
            header_text = header_area.extract_text()
            
            date = extract_date(header_text)
            if date: return date

            # 2. SECONDARY SEARCH: Line-by-Line (better for scanned text)
            # Looks for any line in the top area containing 'Date'
            lines = header_area.extract_text_lines()
            for line in lines:
                date = extract_date(line['text'])
                if date: return date

            # 3. FALLBACK: Bottom area (Signature section)
            footer_box = (0, height * 0.75, width, height)
            footer_text = first_page.within_bbox(footer_box).extract_text()
            return extract_date(footer_text)
            
    except Exception as e:
        if "No /Root object" not in str(e):
            logger.warning(f"PDF Extraction Error: {pdf_url} | {e}")
        return None