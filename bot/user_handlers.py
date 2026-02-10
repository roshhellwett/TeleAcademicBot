from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from database.db import SessionLocal
from database.models import Subscriber, Notification


# ================= START =================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()

    tg = str(update.effective_user.id)

    sub = db.query(Subscriber).filter_by(telegram_id=tg).first()

    if not sub:
        db.add(Subscriber(telegram_id=tg, active=True))
        db.commit()

    await update.message.reply_text(
        "TELEACADEMIC BOT ACTIVE\n\nYou will receive MAKAUT updates automatically."
    )

    db.close()


# ================= SUBSCRIBE =================
async def subscribe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()
    tg = str(update.effective_user.id)

    sub = db.query(Subscriber).filter_by(telegram_id=tg).first()

    if sub:
        sub.active = True
    else:
        db.add(Subscriber(telegram_id=tg, active=True))

    db.commit()
    db.close()

    await update.message.reply_text("SUBSCRIPTION ENABLED")


# ================= UNSUBSCRIBE =================
async def unsubscribe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()
    tg = str(update.effective_user.id)

    sub = db.query(Subscriber).filter_by(telegram_id=tg).first()

    if sub:
        sub.active = False
        db.commit()

    db.close()

    await update.message.reply_text("SUBSCRIPTION DISABLED")


# ================= LATEST =================
async def latest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()

    rows = (
        db.query(Notification)
        .order_by(Notification.scraped_at.desc())
        .limit(5)
        .all()
    )

    if not rows:
        await update.message.reply_text("NO DATA YET")
        db.close()
        return

    msg = "LATEST MAKAUT NOTIFICATIONS\n\n"

    for r in rows:
        msg += f"{r.title}\n{r.source_url}\n\n"

    await update.message.reply_text(msg)

    db.close()


# ================= STATUS =================
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("BOT RUNNING")


# ================= HELP =================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "/start\n"
        "/subscribe\n"
        "/unsubscribe\n"
        "/latest\n"
        "/status\n"
        "/help"
    )


# ================= REGISTER =================
def register_user_handlers(app):

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("subscribe", subscribe_cmd))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_cmd))
    app.add_handler(CommandHandler("latest", latest_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
#@roshhellwett makaut tele bot