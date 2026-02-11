import asyncio
import logging

from bot.telegram_app import build_app
from pipeline.ingest_pipeline import start_pipeline
from database.init_db import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("MAIN")


async def main():

    logger.info("🚀 TELEACADEMIC BOT STARTING")

    init_db()
    logger.info("DATABASE READY")

    # Build telegram app
    app = build_app()

    # Start pipeline in background
    asyncio.create_task(start_pipeline())

    logger.info("PIPELINE BACKGROUND TASK STARTED")

    # Telegram takes control of loop
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
