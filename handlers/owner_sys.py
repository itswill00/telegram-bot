import logging
import os
import html
from telegram import Update
from telegram.ext import ContextTypes


from utils.config import OWNER_ID
from database.system_db import get_setting, set_setting
from utils.backup import backup_database

logger = logging.getLogger(__name__)

async def sys_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if not msg or not user or user.id not in OWNER_ID:
        return

    if not context.args:
        backup = await get_setting("auto_backup", "ON")
        maint = await get_setting("maintenance_mode", "OFF")
        ai = await get_setting("ai_global", "ON")

        status_text = (
            "<b>SYSTEM_CONTROL_PANEL</b>\n\n"
            "<code>"
            f"AUTO_BACKUP : {backup}\n"
            f"MAINTENANCE : {maint}\n"
            f"AI_GLOBAL   : {ai}"
            "</code>\n\n"
            "<b>OPERATIONS:</b>\n"
            "• <code>$node backup [on|off]</code>\n"
            "• <code>$node maintenance [on|off]</code>\n"
            "• <code>$node ai [on|off]</code>\n"
            "• <code>$node logs [line_count]</code>"
        )
        return await msg.reply_text(status_text, parse_mode="HTML")


    action = context.args[0].lower()

    if action == "logs":
        try:
            count = int(context.args[1]) if len(context.args) > 1 else 20
            if count > 100: count = 100
        except Exception:
            count = 20

        if not os.path.exists("bot.log"):
            return await msg.reply_text("ERROR: LOG_NOT_FOUND", parse_mode="HTML")

        try:
            import subprocess
            # Use tail if on linux/mac, or read last lines manually
            if os.name == 'posix':
                out = subprocess.check_output(["tail", "-n", str(count), "bot.log"]).decode('utf-8', errors='ignore')
            else:
                with open("bot.log", "r", encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    out = "".join(lines[-count:])

            if not out.strip():
                return await msg.reply_text("ERROR: LOG_EMPTY", parse_mode="HTML")

            header = f"<b>SYSTEM_LOG (Last {count} lines)</b>\n"
            return await msg.reply_text(f"{header}<code>{html.escape(out[-3900:])}</code>", parse_mode="HTML")
        except Exception as e:
            return await msg.reply_text(f"ERROR: {e}", parse_mode="HTML")

    if len(context.args) < 2:
        return await msg.reply_text("ERROR: Target state required (on/off).", parse_mode="HTML")
    
    val = context.args[1].upper()
    if val not in ("ON", "OFF"):
        return await msg.reply_text("ERROR: Invalid state.", parse_mode="HTML")

    if action == "backup":
        await set_setting("auto_backup", val)
        if val == "OFF":
            jobs = context.application.job_queue.get_jobs_by_name("auto_backup")
            for job in jobs: job.schedule_removal()
            text = "SUCCESS: AUTO_BACKUP routine suspended."
        else:
            context.application.job_queue.run_repeating(backup_database, interval=60 * 60 * 12, first=10, name="auto_backup")
            text = "SUCCESS: AUTO_BACKUP routine scheduled (12h)."
        return await msg.reply_text(text, parse_mode="HTML")

    if action == "maintenance":
        await set_setting("maintenance_mode", val)
        text = f"SUCCESS: MAINTENANCE set to {val}."
        return await msg.reply_text(text, parse_mode="HTML")

    if action == "ai":
        await set_setting("ai_global", val)
        text = f"SUCCESS: AI_GLOBAL set to {val}."
        return await msg.reply_text(text, parse_mode="HTML")

    return await msg.reply_text("ERROR: Module undefined.", parse_mode="HTML")

