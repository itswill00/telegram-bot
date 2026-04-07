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
        # Show system status
        backup = get_setting("auto_backup", "ON")
        maint = get_setting("maintenance_mode", "OFF")
        ai = get_setting("ai_global", "ON")

        status_text = (
            "🛠 <b>System Control Panel</b>\n\n"
            f"🔄 <b>Auto Backup:</b> <code>{backup}</code>\n"
            f"🚧 <b>Maintenance:</b> <code>{maint}</code>\n"
            f"🤖 <b>Global AI:</b> <code>{ai}</code>\n\n"
            "<b>Commands:</b>\n"
            "• <code>$sys backup on|off</code>\n"
            "• <code>$sys maintenance on|off</code>\n"
            "• <code>$sys ai on|off</code>"
        )
        return await msg.reply_text(status_text, parse_mode="HTML")

    action = context.args[0].lower()
    if len(context.args) < 2:
        return await msg.reply_text("❌ Usage: <code>$sys <feature> on|off</code>", parse_mode="HTML")
    
    val = context.args[1].upper()
    if val not in ("ON", "OFF"):
        return await msg.reply_text("❌ Value must be <b>ON</b> or <b>OFF</b>.", parse_mode="HTML")

    if action == "backup":
        set_setting("auto_backup", val)
        if val == "OFF":
            # Remove from job queue
            jobs = context.application.job_queue.get_jobs_by_name("auto_backup")
            for job in jobs:
                job.schedule_removal()
            text = "✅ <b>Auto Backup: DISABLED</b>\nExisting backup tasks removed."
        else:
            # Re-schedule in job queue
            context.application.job_queue.run_repeating(
                backup_database, 
                interval=60 * 60 * 12, # 12 hours
                first=10,
                name="auto_backup"
            )
            text = "✅ <b>Auto Backup: ENABLED</b>\nScheduled every 12 hours."
        
        return await msg.reply_text(text, parse_mode="HTML")

    if action == "maintenance":
        set_setting("maintenance_mode", val)
        text = f"✅ <b>Maintenance Mode: {val}</b>\nNon-admin users will be blocked."
        return await msg.reply_text(text, parse_mode="HTML")

    if action == "ai":
        set_setting("ai_global", val)
        text = f"✅ <b>Global AI: {val}</b>\nAll AI services (Groq/Gemini) toggled."
        return await msg.reply_text(text, parse_mode="HTML")

    return await msg.reply_text("❌ Unknown feature.", parse_mode="HTML")
