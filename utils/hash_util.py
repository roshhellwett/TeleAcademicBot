import hashlib


def generate_hash(title: str, url: str) -> str:
    """
    Generate unique hash for notification
    """
    raw = f"{title}|{url}"
    return hashlib.sha256(raw.encode()).hexdigest()
#@roshhellwett makaut tele bot