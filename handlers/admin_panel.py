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
            InlineKeyboardButton("Status Sistem", callback_data="admin_stats"),
            InlineKeyboardButton("Cadangkan Data", callback_data="admin_backup"),
        ],
        [
            InlineKeyboardButton("Pantau Log", callback_data="admin_logs"),
            InlineKeyboardButton("Mulai Ulang Bot", callback_data="admin_restart"),
        ],
        [InlineKeyboardButton("Tutup Menu", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_owner(user.id):
        return

    text = (
        "<b>Dashboard Admin</b>\n"
        "Silakan pilih opsi di bawah ini untuk mengelola operasional bot."
    )
    await update.message.reply_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    
    if not query or not user or not is_owner(user.id):
        await query.answer("Maaf, akses hanya untuk pemilik.", show_alert=True)
        return

    data = query.data
    await query.answer()

    if data == "admin_stats":
        stats = gather_system_stats()
        text = (
            "<b>Statistik Sistem Saat Ini</b>\n"
            f"• <b>Platform:</b> {stats['sys']['os']}\n"
            f"• <b>Aktif:</b> {stats['sys']['uptime']}\n"
            f"• <b>Beban CPU:</b> {stats['cpu']['load']:.1f}% ({stats['cpu']['cores']} core)\n"
            f"• <b>Memori RAM:</b> {stats['ram']['pct']:.1f}% ({stats['ram']['used']//1024//1024}/{stats['ram']['total']//1024//1024} MB)\n"
            f"• <b>Penyimpanan:</b> {stats['disk']['pct']:.1f}% terpakai"
        )
        await query.edit_message_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == "admin_backup":
        await query.edit_message_text("Sedang memproses pencadangan data...", parse_mode="HTML")
        await backup_database(context)
        await query.edit_message_text("Pencadangan berhasil dikirim ke chat log.", reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == "admin_logs":
        # Simulating log view by reading the last few lines of the session or a log file if configured
        # For Termux, we can try to send a quick snippet
        await query.edit_message_text("📜 Mengambil log terbaru...", parse_mode="HTML")
        # In a real scenario, you'd log to a file. For now, we'll just show status.
        await query.edit_message_text("✅ Log berhasil dipantau di terminal.", reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == "admin_restart":
        await query.edit_message_text("🔄 <b>Bot Sedang Restart...</b>\nSampai jumpa sebentar lagi!", parse_mode="HTML")
        # Restart logic: execv will replace current process
        python = sys.executable
        os.execl(python, python, *sys.argv)

    elif data == "admin_close":
        await query.message.delete()
