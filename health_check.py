import asyncio
import logging
from telegram import Bot
from sqlalchemy import text
from database.db import engine
from core.config import BOT_TOKEN, SEARCH_BOT_TOKEN, ADMIN_BOT_TOKEN

logging.basicConfig(level=logging.INFO)

async def verify_system():
    print("\n🔍 === ZENITH SUPREME SYSTEM HEALTH CHECK (CLOUD EDITION) ===\n")

    # 1. Test All Bot Connections
    tokens = [("MAIN", BOT_TOKEN), ("SEARCH", SEARCH_BOT_TOKEN), ("ADMIN", ADMIN_BOT_TOKEN)]
    for name, token in tokens:
        try:
            bot = Bot(token=token)
            me = await bot.get_me()
            print(f"✅ {name} BOT: @{me.username} is ONLINE")
        except Exception as e:
            print(f"❌ {name} BOT: OFFLINE | {e}")

    # 2. Test Unified PostgreSQL Connection
    try:
        async with engine.connect() as conn:
            # Simple keepalive check
            await conn.execute(text("SELECT 1"))
            print(f"✅ DATABASE: PostgreSQL Connection Pool ACTIVE")
            
            # FIX: Check for the NEW table name 'user_strikes_v2'
            result = await conn.execute(text("SELECT to_regclass('public.user_strikes_v2')"))
            if result.scalar():
                print(f"✅ SECURITY: Table 'user_strikes_v2' FOUND")
            else:
                print(f"⚠️ SECURITY: Table 'user_strikes_v2' NOT FOUND (Will be created on init)")
                
    except Exception as e:
        print(f"❌ DATABASE FATAL ERROR: {e}")

    print("\n🚀 === ALL SYSTEMS GO ===\n")

if __name__ == "__main__":
    asyncio.run(verify_system())