import asyncio
import logging

from scraper.makaut_scraper import scrape_all_sources
from database.db import SessionLocal
from database.models import Notification
from delivery.broadcaster import broadcast
from core.config import SCRAPE_INTERVAL

logger = logging.getLogger("PIPELINE")


async def start_pipeline():

    while True:
        try:
            logger.info("SCRAPE CYCLE START")

            items = scrape_all_sources()
            logger.info(f"SCRAPED {len(items)} ITEMS")

            db = SessionLocal()

            # ===== EXISTING HASHES (LOW DB LOAD) =====
            existing_hashes = set(
                h[0] for h in db.query(Notification.content_hash).all()
            )

            new_notifications = []

            for item in items:
                try:
                    h = item.get("content_hash")
                    if not h:
                        continue

                    if h in existing_hashes:
                        continue

                    notif = Notification(**item)
                    db.add(notif)

                    new_notifications.append(item)
                    existing_hashes.add(h)

                except Exception as item_error:
                    logger.warning(f"BAD ITEM {item_error}")

            db.commit()
            db.close()

            logger.info(f"PIPELINE STORED {len(new_notifications)} NEW")

            # ===== AUTO BROADCAST ONLY NEW =====
            if new_notifications:
                await broadcast(new_notifications)

        except Exception as e:
            logger.error(f"PIPELINE ERROR {e}")

        logger.info("SCRAPE CYCLE DONE")
        await asyncio.sleep(SCRAPE_INTERVAL)
#@roshhellwett makaut tele bot