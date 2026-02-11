import logging
from telegram.ext import ApplicationBuilder

from core.config import BOT_TOKEN
from bot.user_handlers import register_user_handlers

logger = logging.getLogger("TELEGRAM")

_app = None


def get_bot():
    if _app is None:
        raise RuntimeError("Bot not ready")
    return _app.bot


def build_app():
    global _app

    logger.info("BUILDING TELEGRAM APP")

    _app = ApplicationBuilder().token(BOT_TOKEN).build()

    register_user_handlers(_app)

    logger.info("HANDLERS REGISTERED")

    return _app
