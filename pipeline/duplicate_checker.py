from database.db import SessionLocal
from database.models import Notification

def is_duplicate(hash_value):
    db = SessionLocal()
    exists = db.query(Notification).filter(
        Notification.content_hash == hash_value
    ).first()
    db.close()
    return exists is not None
#@roshhellwett makaut tele bot