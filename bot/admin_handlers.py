from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

ADMIN_ID = "7940390110"


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return

    await update.message.reply_text("ADMIN PANEL")


async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return

    await update.message.reply_text("BROADCAST PANEL READY")


def register_admin_handlers(app):
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
#@roshhellwett makaut tele bot