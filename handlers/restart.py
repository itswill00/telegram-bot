import os
import sys
import json
import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.config import OWNER_ID

log = logging.getLogger(__name__)

RESTART_FILE = "data/restart.json"

async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if not msg or not user or user.id not in OWNER_ID:
        return

    m = await msg.reply_text(
        "<b>SYSTEM REBOOT INITIALIZED</b>\n"
        "Killing active process and respawning...",
        parse_mode="HTML"
    )

    # Save state to notify after restart
    data = {
        "chat_id": msg.chat_id,
        "msg_id": m.message_id
    }
    
    os.makedirs("data", exist_ok=True)
    with open(RESTART_FILE, "w") as f:
        json.dump(data, f)

    log.info(f"Rebooting process... (Signal from {user.id})")
    
    sys.stdout.flush()
    sys.stderr.flush()

    os.execv(sys.executable, [sys.executable] + sys.argv)

