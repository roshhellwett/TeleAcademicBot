import re
from datetime import datetime

def extract_date(text, pdf_url=None):
    patterns = [
        r'\d{1,2}[-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]?\d{2,4}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
    ]

    for p in patterns:
        m = re.search(p, text or "")
        if m:
            try:
                return datetime.strptime(m.group(), "%d %b %Y")
            except:
                pass

    # PDF filename date fallback
    if pdf_url:
        m = re.search(r'20\d{2}', pdf_url)
        if m:
            return datetime(int(m.group()), 1, 1)

    return None
#@roshhellwett makaut tele bot