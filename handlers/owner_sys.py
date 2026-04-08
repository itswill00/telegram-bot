import logging
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
            "<b>SYSTEM CONTROL PANEL</b>\n\n"
            f"AUTO_BACKUP: <code>{backup}</code>\n"
            f"MAINTENANCE: <code>{maint}</code>\n"
            f"AI_GLOBAL: <code>{ai}</code>\n\n"
            "<b>OPERATIONS:</b>\n"
            "• $sys backup on|off\n"
            "• $sys maintenance on|off\n"
            "• $sys ai on|off"
        )
        return await msg.reply_text(status_text, parse_mode="HTML")

    action = context.args[0].lower()
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
            text = "SUCCESS: Auto-backup routine suspended."
        else:
            context.application.job_queue.run_repeating(backup_database, interval=60 * 60 * 12, first=10, name="auto_backup")
            text = "SUCCESS: Auto-backup routine scheduled (12h)."
        return await msg.reply_text(text, parse_mode="HTML")

    if action == "maintenance":
        await set_setting("maintenance_mode", val)
        text = f"SUCCESS: Maintenance mode set to {val}."
        return await msg.reply_text(text, parse_mode="HTML")

    if action == "ai":
        await set_setting("ai_global", val)
        text = f"SUCCESS: Global AI availability set to {val}."
        return await msg.reply_text(text, parse_mode="HTML")

    return await msg.reply_text("ERROR: Module undefined.", parse_mode="HTML")
