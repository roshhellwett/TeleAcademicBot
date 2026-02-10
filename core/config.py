import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///telebot.db"
)

ADMIN_ID = int(os.getenv("ADMIN_ID", "7940390110"))

SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "300"))
#@roshhellwett makaut tele bot