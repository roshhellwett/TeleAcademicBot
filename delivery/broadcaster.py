from database.db import SessionLocal
from database.models import Subscriber
from pipeline.message_formatter import format_message
from bot.telegram_app import get_bot


async def broadcast(notifications):

    bot = get_bot()

    db = SessionLocal()
    users = db.query(Subscriber).filter(Subscriber.active == True).all()

    for n in notifications:
        msg = format_message(n)

        for u in users:
            try:
                await bot.send_message(u.telegram_id, msg, disable_web_page_preview=True)
            except:
                pass

    db.close()
#@roshhellwett makaut tele bot