from bot.telegram_app import get_bot
from database.db import SessionLocal
from database.models import Subscriber


def run_health_check():

    print("=== TELEACADEMIC HEALTH CHECK ===")

    # DB
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        print("DB OK")
        db.close()
    except Exception as e:
        print("DB FAIL", e)

    # Telegram
    try:
        bot = get_bot()
        print("TELEGRAM OK", bot.username)
    except Exception as e:
        print("TELEGRAM FAIL", e)

    # Subscribers
    try:
        db = SessionLocal()
        count = db.query(Subscriber).count()
        print("SUBSCRIBERS:", count)
        db.close()
    except Exception as e:
        print("SUBSCRIBER CHECK FAIL", e)
