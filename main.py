import asyncio
import logging
import sys
import signal

from core.logger import setup_logger
from database.init_db import init_db
from bot.telegram_app import start_telegram
from pipeline.ingest_pipeline import start_pipeline
from search_bot.search_app import start_search_bot 
from admin_bot.admin_app import start_admin_bot 
from group_bot.group_app import start_group_bot
from core.task_manager import supervised_task

setup_logger()
logger = logging.getLogger("MAIN")

async def shutdown(signal, loop):
    logger.info(f"🛑 Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    logger.info("🚀 ZENITH SUPREME: CLOUD BOOT SEQUENCE INITIALIZED")

    # 1. Infrastructure Check
    try:
        await init_db()
        await start_telegram()
    except Exception as e:
        logger.critical(f"💀 FATAL BOOT FAILURE: {e}")
        return

    # 2. Signal Handlers (For Railway Graceful Shutdown)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))

    # 3. Launch Cluster
    tasks = [
        asyncio.create_task(supervised_task("SEARCH_BOT", start_search_bot)),
        asyncio.create_task(supervised_task("ADMIN_BOT", start_admin_bot)),
        asyncio.create_task(supervised_task("GROUP_BOT", start_group_bot)),
        asyncio.create_task(supervised_task("PIPELINE", start_pipeline))
    ]
    
    logger.info("✅ ALL SYSTEMS OPERATIONAL. MONITORING ACTIVE.")
    
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("👋 System Shutdown Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        #@academictelebotbyroshhellwett