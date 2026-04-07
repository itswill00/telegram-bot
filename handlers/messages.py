from telegram.ext import MessageHandler, filters

from utils.logger import log_commands
from handlers.collector import collect_chat
from handlers.delete import reply_del_handler
from handlers.dl.handlers import auto_dl_detect
from handlers.bot_dollar import dollar_router
from handlers.welcome import welcome_handler
from utils.user_collector import user_collector
from handlers.groq import groq_query, _GROQ_ACTIVE_USERS
from handlers.gemini import ai_cmd, _AI_ACTIVE_USERS
from database.system_db import get_setting
from utils.config import OWNER_ID

async def maintenance_filter(update, context):
    user = update.effective_user
    if user.id in OWNER_ID:
        return False

    maint = get_setting("maintenance_mode", "OFF")
    if maint == "ON":
        await update.message.reply_text(
            "<b>STATUS: SYSTEM MAINTENANCE</b>\n\n"
            "Server is currently undergoing scheduled updates. Access restricted.",
            parse_mode="HTML"
        )
        return True
    return False

async def ai_reply_router(update, context):
    msg = update.message
    if not msg or not msg.reply_to_message:
        return

    if await maintenance_filter(update, context):
        return

    if get_setting("ai_global", "ON") == "OFF":
        return await msg.reply_text("<b>SYSTEM:</b> AI engines are currently offline.")

    user_id = msg.from_user.id
    reply_mid = msg.reply_to_message.message_id

    if _GROQ_ACTIVE_USERS.get(user_id) == reply_mid:
        return await groq_query(update, context)

    if _AI_ACTIVE_USERS.get(user_id) == reply_mid:
        return await ai_cmd(update, context)

    if reply_mid in _GROQ_ACTIVE_USERS.values():
        return await msg.reply_text(
            "<b>UNAUTHORIZED:</b>\n"
            "Active session required. Initialize with /groq.",
            parse_mode="HTML"
        )

    if reply_mid in _AI_ACTIVE_USERS.values():
        return await msg.reply_text(
            "<b>UNAUTHORIZED:</b>\n"
            "Active session required. Initialize with /ask.",
            parse_mode="HTML"
        )

    return

async def global_maint_check(update, context):
    await maintenance_filter(update, context)

def register_messages(app):
    app.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, global_maint_check),
        group=-2,
    )

    app.add_handler(
        MessageHandler(filters.ALL, collect_chat),
        group=0,
    )

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_handler),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & filters.REPLY, reply_del_handler),
        group=2,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, dollar_router),
        group=3,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_dl_detect),
        group=4,
    )

    app.add_handler(
        MessageHandler(filters.ALL, log_commands),
        group=99,
    )
    
    app.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, user_collector),
        group=1
    )
    
    app.add_handler(
        MessageHandler(filters.REPLY & filters.TEXT & ~filters.COMMAND, ai_reply_router),
        group=-1
    )
