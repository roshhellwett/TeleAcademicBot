import re
from datetime import datetime

# Specific patterns for MAKAUT official headers
DATE_PATTERNS = [
    # Strictly matches "Date: 06-01-2026" or "Date: 16.01.2026"
    r"Date[:\s]*(\d{2}[-/\.]\d{2}[-/\.]\d{4})",
    # Matches "Dated: 20.06.2024"
    r"Dated?[:\s]*(\d{2}[-/\.]\d{2}[-/\.]\d{4})",
    # Standalone DD-MM-YYYY
    r"(\d{2}[-/\.]\d{2}[-/\.]\d{4})"
]

def extract_date(text: str):
    if not text:
        return None

    # Clean text: remove extra spaces and common PDF artifacts
    clean_text = " ".join(text.split()).strip()

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            date_str = match.group(1) if "(" in pattern else match.group()
            
            # Normalize separators
            normalized = date_str.replace("-", "/").replace(".", "/")
            
            try:
                dt = datetime.strptime(normalized, "%d/%m/%Y")
                # CRITICAL: Ignore dates older than 2024 to avoid "legacy notice" mistakes
                if dt.year >= 2024:
                    return dt
            except ValueError:
                continue
    return None