from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now().strftime("%d %b %Y %I:%M %p")

    text = f"""
SYSTEM STATUS: ACTIVE

LAST CHECK: {now}
SYNC MODE: AUTOMATIC
SCRAPER: RUNNING
DELIVERY: READY

If no message received:
→ No new official notification found
"""

    await update.message.reply_text(text)
#@roshhellwett makaut tele bot