import asyncio
import logging
from scraper.makaut_scraper import scrape_source
from core.sources import URLS
from database.repository import NotificationRepo
from delivery.channel_broadcaster import broadcast_channel
from pipeline.message_formatter import format_message
from core.config import SCRAPE_INTERVAL

logger = logging.getLogger("PIPELINE")

async def start_pipeline():
    logger.info("🚀 PIPELINE: STARTED (Ordering: Oldest -> Newest)")
    
    while True:
        cycle_start = asyncio.get_event_loop().time()
        
        for key, config in URLS.items():
            try:
                # 1. Scrape (Returns Newest First usually)
                items = await scrape_source(key, config)
                
                if not items:
                    continue

                # 2. CRITICAL: Reverse order to process Oldest first
                items.reverse()
                
                new_notices = []
                for item in items:
                    # 3. Check DB (Idempotent)
                    is_new = await NotificationRepo.add_notification(item)
                    if is_new:
                        logger.info(f"📥 NEW: {item['title'][:30]}...")
                        new_notices.append(format_message(item))
                
                # 4. Broadcast (Oldest -> Newest)
                if new_notices:
                    await broadcast_channel(new_notices)
                
                await asyncio.sleep(2)  # Nice to University Server

            except Exception as e:
                logger.error(f"❌ PIPELINE ERROR [{key}]: {e}")

        # Smart Sleep
        elapsed = asyncio.get_event_loop().time() - cycle_start
        sleep_time = max(10, SCRAPE_INTERVAL - elapsed)
        logger.info(f"💤 Sleeping {int(sleep_time)}s...")
        await asyncio.sleep(sleep_time)
        #@academictelebotbyroshhellwett