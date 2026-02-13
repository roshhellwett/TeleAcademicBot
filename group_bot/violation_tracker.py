import logging
from datetime import datetime
from sqlalchemy import select
from database.db import AsyncSessionLocal  # Shared Session
from database.security_models import UserStrike

logger = logging.getLogger("VIOLATION_TRACKER")
STRIKE_LIMIT = 3

async def add_strike(user_id: int) -> bool:
    """Adds a strike to the persistent PostgreSQL DB."""
    async with AsyncSessionLocal() as db:
        try:
            stmt = select(UserStrike).where(UserStrike.user_id == user_id)
            result = await db.execute(stmt)
            record = result.scalar_one_or_none()

            if not record:
                record = UserStrike(user_id=user_id, strike_count=1, last_violation=datetime.utcnow())
                db.add(record)
                await db.commit()
                return False
            
            record.strike_count += 1
            record.last_violation = datetime.utcnow()
            
            should_ban = record.strike_count >= STRIKE_LIMIT
            if should_ban:
                record.strike_count = 0  # Reset for next cycle (or keep logic as per preference)
            
            await db.commit()
            return should_ban

        except Exception as e:
            logger.error(f"⚠️ Strike Tracking Failed: {e}")
            return False
            #@academictelebotbyroshhellwett