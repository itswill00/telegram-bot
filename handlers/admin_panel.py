import os
import sys
import time
import asyncio
import logging
import platform
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.config import OWNER_ID, LOG_CHAT_ID
from utils.backup import backup_database
from handlers.stats.system_info import gather_system_stats

logger = logging.getLogger(__name__)

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_ID

def get_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("STATUS_CHECK", callback_data="admin_stats"),
            InlineKeyboardButton("BACKUP_RT", callback_data="admin_backup"),
        ],
        [
            InlineKeyboardButton("GET_LOGS", callback_data="admin_logs"),
            InlineKeyboardButton("NODE_REBOOT", callback_data="admin_restart"),
        ],
        [InlineKeyboardButton("EXIT_SESSION", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_owner(user.id):
        return

    text = (
        "<b>CORE INTERFACE</b>\n"
        "Awaiting instruction:"
    )
    await update.message.reply_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    
    if not query or not user or not is_owner(user.id):
        await query.answer("ERROR: UNAUTHORIZED", show_alert=True)
        return

    data = query.data
    await query.answer()

    if data == "admin_stats":
        stats = gather_system_stats()
        text = (
            "<b>SYSTEM TOPOLOGY</b>\n"
            "<code>"
            f"PLATFORM : {stats['sys']['os']}\n"
            f"UPTIME   : {stats['sys']['uptime']}\n"
            f"CPU LOAD : {stats['cpu']['load']:.1f}% ({stats['cpu']['cores']} cores)\n"
            f"RAM LOAD : {stats['ram']['pct']:.1f}% ({stats['ram']['used']//1024//1024}/{stats['ram']['total']//1024//1024} MB)\n"
            f"STORAGE  : {stats['disk']['pct']:.1f}%"
            "</code>"
        )

        await query.edit_message_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == "admin_backup":
        await query.edit_message_text("<b>EXECUTING_BACKUP...</b>", parse_mode="HTML")
        await backup_database(context)
        await query.edit_message_text("<b>BACKUP_SUCCESS</b>", reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == "admin_logs":
        await query.edit_message_text("<b>FETCHING_LOGS...</b>", parse_mode="HTML")
        await query.edit_message_text("<b>LOG_READY</b>\nOutput piped to log terminal.", reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == "admin_restart":
        await query.edit_message_text("<b>REBOOT_INITIATED</b>\nRestarting main process...", parse_mode="HTML")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    elif data == "admin_close":
        await query.message.delete()

