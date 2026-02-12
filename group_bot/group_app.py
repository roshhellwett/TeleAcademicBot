import os
import logging
import asyncio
import time
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from group_bot.filters import is_inappropriate
from group_bot.flood_control import is_flooding
from group_bot.violation_tracker import add_strike, MUTE_DURATION_SECONDS
from core.config import ADMIN_ID

logger = logging.getLogger("GROUP_BOT")

# Performance Config for High-Traffic (2000+ members)
WELCOME_COOLDOWN = 30  
last_welcome_time = 0

async def start_group_bot():
    token = os.getenv("GROUP_BOT_TOKEN")
    if not token:
        logger.error("GROUP_BOT_TOKEN missing!")
        return

    # Build app with optimized concurrency settings for large groups
    app = ApplicationBuilder().token(token).read_timeout(30).connect_timeout(30).build()

    async def send_welcome_hub(chat_id, context: ContextTypes.DEFAULT_TYPE):
        """Standardized Hub Menu for Channel and Search Bot."""
        keyboard = [
            [InlineKeyboardButton("📢 Official Notification Channel", url="https://t.me/teleacademicbot")],
            [InlineKeyboardButton("🔍 Search Past Notices (Search Bot)", url="https://t.me/makautsearchbot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "🎓 <b>Academic Group & Rules</b>\n\n"
            "<b>Quick Links:</b>\n"
            "1. Check the <b>Channel</b> for real-time alerts.\n"
            "2. Use the <b>Search Bot</b> to find specific documents.\n\n"
            "⚖️ <b>Group Rules:</b>\n"
            "• No abusive language or personal attacks.\n"
            "• No spamming or unauthorized links.\n"
            "* MAKAUT UNIVERSITY HAS BEEN INTEGRATED *"
        )
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=reply_markup)

    async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Throttled Welcome Logic with 20-second Auto-Deletion."""
        global last_welcome_time
        now = time.time()

        if now - last_welcome_time > WELCOME_COOLDOWN:
            last_welcome_time = now
            
            # Send the welcome hub
            welcome_msg = await send_welcome_hub(update.effective_chat.id, context)
            
            # Background task to delete the message after 20 seconds
            async def auto_delete():
                await asyncio.sleep(20)
                try:
                    await welcome_msg.delete()
                except Exception as e:
                    logger.debug(f"Welcome message already removed: {e}")

            asyncio.create_task(auto_delete())

    async def help_hub(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manual /help command. These stay permanent unless manually removed."""
        await send_welcome_hub(update.effective_chat.id, context)

    async def group_monitor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Forensic Message Monitor with Strike Enforcement and Admin Hygiene."""
        if not update.message or not update.message.text:
            return

        text = update.message.text
        user = update.effective_user
        chat_id = update.effective_chat.id
        chat_title = update.effective_chat.title or "Academic Group"

        # 1. Forensic Scans (Abuse & Flood) using pre-compiled engine
        violation, reason = await is_inappropriate(text)
        if not violation:
            violation, reason = is_flooding(user.id, text)

        if violation:
            try:
                await update.message.delete()
                
                # Await database-backed strike counter
                hit_limit = await add_strike(user.id)
                
                if hit_limit:
                    until_date = int(time.time() + MUTE_DURATION_SECONDS)
                    await context.bot.restrict_chat_member(
                        chat_id=chat_id, 
                        user_id=user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=until_date
                    )
                    
                    admin_report = (
                        f"🛡️ <b>SECURITY ALERT: USER MUTED</b>\n"
                        f"<b>Group:</b> {chat_title}\n"
                        f"<b>User:</b> @{user.username} (<code>{user.id}</code>)\n"
                        f"<b>Reason:</b> {reason}"
                    )
                    
                    # Send alert to Admin and schedule auto-cleanup
                    report_msg = await context.bot.send_message(chat_id=ADMIN_ID, text=admin_report, parse_mode="HTML")
                    
                    async def clean_admin_report():
                        await asyncio.sleep(3600) # Deletes report after 1 hour
                        try:
                            await report_msg.delete()
                        except:
                            pass
                    asyncio.create_task(clean_admin_report())

                    msg_text = f"🚫 <b>SUPREME MUTE</b>\nUser: @{user.username}\nAction: Restricted for 1 Hour"
                else:
                    msg_text = f"🛡️ <b>MESSAGE DELETED</b>\nUser: @{user.username}\nReason: {reason}"

                warn_msg = await context.bot.send_message(chat_id=chat_id, text=msg_text, parse_mode="HTML")
                
                # Auto-delete enforcement warnings after 10 seconds
                await asyncio.sleep(10)
                await warn_msg.delete()
            except Exception as e:
                logger.error(f"Enforcement Error: {e}")

    # Handler Registration
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_handler))
    app.add_handler(CommandHandler("help", help_hub))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, group_monitor_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("ACADEMIC HUB ONLINE: HIGH-TRAFFIC MODE ACTIVE")
#@academictelebotbyroshhellwett