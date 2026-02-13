import os
import logging
from dotenv import load_dotenv

# Load local .env for testing, but Railway env vars take precedence
load_dotenv()

# ==============================
# TELEGRAM TOKENS
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
SEARCH_BOT_TOKEN = os.getenv("SEARCH_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
GROUP_BOT_TOKEN = os.getenv("GROUP_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    raise ValueError("❌ FATAL: BOT_TOKEN is missing from Environment Variables.")

# ==============================
# CLOUD DATABASE CONFIGURATION
# ==============================
# Railway provides 'postgres://', but SQLAlchemy requires 'postgresql+asyncpg://'
_RAW_DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///local_backup.db")

if _RAW_DB_URL.startswith("postgres://"):
    DATABASE_URL = _RAW_DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif _RAW_DB_URL.startswith("postgresql://"):
    DATABASE_URL = _RAW_DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _RAW_DB_URL

# ==============================
# PIPELINE SETTINGS
# ==============================
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "300"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TARGET_YEAR = 2025
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==============================
# SECURITY & LIMITS
# ==============================
SSL_VERIFY_EXEMPT = ["makautexam.net", "www.makautexam.net"]
REQUEST_TIMEOUT = 30.0
MAX_PDF_SIZE_MB = 10  # RAM Safety Limit  # Memory guard to prevent OOM crashes [cite: 45]
#@academictelebotbyroshhellwett