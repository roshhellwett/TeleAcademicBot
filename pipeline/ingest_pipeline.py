import asyncio
import logging
from datetime import datetime

from scraper.makaut_scraper import scrape_all_sources
from database.db import SessionLocal
from database.models import Notification
from delivery.broadcaster import broadcast
from core.config import SCRAPE_INTERVAL

logger = logging.getLogger("PIPELINE")


async def start_pipeline():

    logger.info("PIPELINE STARTED")

    while True:

        db = None

        try:
            logger.info("SCRAPE CYCLE START")

            items = scrape_all_sources()

            logger.info(f"SCRAPED {len(items)} ITEMS")

            if not items:
                await asyncio.sleep(SCRAPE_INTERVAL)
                continue

            db = SessionLocal()

            existing_hashes = {
                h for (h,) in db.query(Notification.content_hash).all()
            }

            new_notifications = []

            for item in items:

                h = item.get("content_hash")

                if not h or h in existing_hashes:
                    continue

                item.setdefault("scraped_at", datetime.utcnow())
                item.setdefault("published_date", datetime.utcnow())

                notif = Notification(**item)

                db.add(notif)
                new_notifications.append(item)

                existing_hashes.add(h)

            if new_notifications:
                db.commit()

            logger.info(f"PIPELINE STORED {len(new_notifications)} NEW")

            if new_notifications:
                await broadcast(new_notifications)

        except Exception as e:
            logger.error(f"PIPELINE ERROR {e}", exc_info=True)

        finally:
            if db:
                db.close()

        logger.info("SCRAPE CYCLE DONE")

        await asyncio.sleep(SCRAPE_INTERVAL)
