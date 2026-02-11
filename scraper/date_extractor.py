import re
from datetime import datetime

# Patterns specifically tuned for MAKAUT headers and "Dated:" prefixes
DATE_PATTERNS = [
    # Captures "Date: 06-01-2026" or "Dated: 16/01/2026"
    r"Date[sd]?[:\s]*(\d{2}[-/\.]\d{2}[-/\.]\d{4})",
    # Standalone DD-MM-YYYY or DD.MM.YYYY
    r"(\d{2}[-/\.]\d{2}[-/\.]\d{4})",
    # Fallback for YYYY-MM-DD
    r"(\d{4}[-/\.]\d{2}[-/\.]\d{2})"
]

def extract_date(text: str):
    if not text:
        return None

    # Remove extra whitespace and hidden characters common in PDFs
    clean_text = " ".join(text.split()).strip()

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            # Extract only the numbers from the capture group if available
            date_str = match.group(1) if "(" in pattern else match.group()
            
            # Normalize all separators to "/" for unified parsing
            normalized = date_str.replace("-", "/").replace(".", "/")
            
            for fmt in ("%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(normalized, fmt)
                except ValueError:
                    continue
    return None