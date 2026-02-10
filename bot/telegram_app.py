from telegram.ext import ApplicationBuilder

from core.config import BOT_TOKEN
from bot.user_handlers import register_user_handlers


_app = None   # Global app instance


def get_bot():
    """
    Safe accessor for broadcaster / delivery layer
    """
    if _app is None:
        raise RuntimeError("Telegram app not initialized yet")
    return _app.bot


async def start_bot():
    global _app

    _app = ApplicationBuilder().token(BOT_TOKEN).build()

    register_user_handlers(_app)

    print("ALL HANDLERS REGISTERED")

    await _app.initialize()
    await _app.start()
    await _app.updater.start_polling()

    import asyncio
    while True:
        await asyncio.sleep(3600)
#@roshhellwett makaut tele bot