import logging
from database.db import Base, engine
# Must import models so Base knows about them
import database.models  
import database.security_models 

logger = logging.getLogger("DB_INIT")

async def init_db():
    """
    Schema Migration: Creates missing tables in PostgreSQL.
    Safe to run on every startup (idempotent).
    """
    logger.info("🔄 DATABASE: Checking Schema...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ DATABASE: Schema Verified.")
    except Exception as e:
        logger.critical(f"🛑 DATABASE FATAL ERROR: {e}")
        raise e
        #@academictelebotbyroshhellwett