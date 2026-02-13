import logging
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from database.db import AsyncSessionLocal
from database.models import Notification
from database.security_models import UserStrike

logger = logging.getLogger("REPO")

class NotificationRepo:
    @staticmethod
    async def add_notification(data: dict) -> bool:
        """Atomic Insert: Returns True ONLY if hash is new."""
        async with AsyncSessionLocal() as db:
            try:
                # 1. Fast Index Check
                stmt = select(Notification.id).where(Notification.content_hash == data['content_hash'])
                exists = (await db.execute(stmt)).scalar()
                
                if exists:
                    return False

                # 2. Insert
                db.add(Notification(**data))
                await db.commit()
                return True
            except IntegrityError:
                await db.rollback()
                return False
            except Exception as e:
                logger.error(f"⚠️ DB Insert Error: {e}")
                return False

    @staticmethod
    async def get_latest(limit: int = 10):
        async with AsyncSessionLocal() as db:
            stmt = select(Notification).order_by(Notification.published_date.desc()).limit(limit)
            return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def search_query(keyword: str, limit: int = 10):
        async with AsyncSessionLocal() as db:
            stmt = select(Notification).filter(
                Notification.title.ilike(f"%{keyword}%")
            ).order_by(Notification.published_date.desc()).limit(limit)
            return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_stats():
        async with AsyncSessionLocal() as db:
            return (await db.execute(select(func.count(Notification.id)))).scalar()

class SecurityRepo:
    @staticmethod
    async def get_active_strikes():
        async with AsyncSessionLocal() as db:
            return (await db.execute(select(func.count(UserStrike.user_id)))).scalar()
            #@academictelebotbyroshhellwett