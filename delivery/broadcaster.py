import asyncio
import logging

from database.db import SessionLocal
from database.models import Subscriber
from bot.telegram_app import get_bot
from pipeline.message_formatter import format_message

logger = logging.getLogger("BROADCASTER")


async def broadcast(notifications):

    # Wait until telegram ready
    while True:
        try:
            bot = get_bot()
            break
        except:
            logger.info("WAITING TELEGRAM READY...")
            await asyncio.sleep(2)

    db = SessionLocal()

    users = db.query(Subscriber).filter_by(active=True).all()

    success = 0
    failed = 0

    for n in notifications:

        msg = format_message(n)

        for u in users:

            try:
                await bot.send_message(
                    chat_id=u.telegram_id,
                    text=msg,
                    disable_web_page_preview=True
                )

                success += 1
                await asyncio.sleep(0.05)

            except Exception as e:
                failed += 1
                logger.error(f"SEND FAIL {u.telegram_id} {e}")

    db.close()

    logger.info(f"BROADCAST DONE success={success} failed={failed}")
