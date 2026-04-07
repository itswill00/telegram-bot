import html
from telegram import Update
from telegram.ext import ContextTypes

from utils.config import OWNER_ID
from utils.backup import perform_backup

async def direct_backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if not msg or not user or user.id not in OWNER_ID:
        return

    status_msg = await msg.reply_text("<b>INITIALIZING:</b> Database compression sequence...", parse_mode="HTML")

    success = await perform_backup(context.bot, msg.chat_id)

    if success:
        await status_msg.edit_text("<b>SUCCESS:</b> Backup transmitted successfully.", parse_mode="HTML")
    else:
        await status_msg.edit_text("<b>ERROR:</b> Internal backup routine failed.", parse_mode="HTML")
