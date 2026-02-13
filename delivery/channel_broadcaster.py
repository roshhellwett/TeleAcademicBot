import asyncio
import logging
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, Forbidden
from bot.telegram_app import get_bot
from core.config import CHANNEL_ID

logger = logging.getLogger("CHANNEL_BROADCAST")

# Dynamic rate limiting: Stay safely under Telegram's 20 msg/min limit
BASE_DELAY = 4.0  
MAX_RETRIES = 5

async def broadcast_channel(messages):
    """Deliver messages with adaptive retries and session protection."""
    bot = get_bot()
    if not messages:
        return

    sent_count = 0
    for msg in messages:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                # CRITICAL: Increased timeout to 60s for Railway stability
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    read_timeout=60,
                    write_timeout=60
                )
                sent_count += 1
                await asyncio.sleep(BASE_DELAY) 
                break 

            except RetryAfter as e:
                logger.warning(f"⏳ Rate Limit hit: Waiting {e.retry_after}s...")
                await asyncio.sleep(e.retry_after + 2)

            except (TimedOut, NetworkError) as e:
                retries += 1
                # NOW WE SEE THE REAL ERROR MESSAGE
                logger.warning(f"📡 Network retry {retries}/{MAX_RETRIES}: {e}")
                await asyncio.sleep(5)

            except BadRequest as e:
                logger.error(f"❌ CONFIG ERROR: Invalid Channel ID or Message Format. Details: {e}")
                break # Don't retry configuration errors

            except Forbidden as e:
                logger.critical(f"🛑 PERMISSION ERROR: Bot is NOT an Admin in Channel {CHANNEL_ID}. Details: {e}")
                break # Don't retry if we are banned/not admin

            except Exception as e:
                logger.error(f"❌ Critical Broadcast Error: {e}")
                break 

    if sent_count > 0:
        logger.info(f"📢 BATCH COMPLETE: {sent_count} notices broadcasted.")
        #@academictelebotbyroshhellwett