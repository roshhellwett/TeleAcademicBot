import asyncio
import logging

from pipeline.ingest_pipeline import start_pipeline
from bot.telegram_app import start_bot
from database.init_db import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("MAIN")


async def main():

    logger.info("BOT STARTED")

    # ===== INIT DB =====
    init_db()
    logger.info("DATABASE READY")

    # ===== START PIPELINE BACKGROUND =====
    asyncio.create_task(start_pipeline())

    # ===== START TELEGRAM (BLOCKING SAFE) =====
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
#@roshhellwett makaut tele bot