from telegram import Update
from telegram.ext import ContextTypes
from utils.config import OWNER_ID

async def owner_help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if not msg or not user or user.id not in OWNER_ID:
        return

    admin_protocols = [
        "admin", "eval", "sh", "env", "sys", "banuser", "unbanuser",
        "cookies", "moderation", "mute", "unmute", "ban", "unban",
        "kick", "addsudo", "rmsudo", "sudolist", "groups", "update",
        "broadcast", "stats", "restart", "help"
    ]

    public_modules = [
        "start", "settings", "q", "ig", "kang", "net", "donate",
        "kurs", "music", "autodl", "waifu", "premium", "quiz",
        "ship", "reminder", "help", "menu", "ping", "ip",
        "whoisdomain", "domain", "tr", "trlist", "helpowner",
        "wlc", "ask", "groq", "weather", "speedtest", "gsearch", "dl"
    ]

    text = (
        "<b>SYSTEM COMMAND INDEX</b>\n"
        "--- OWNER PRIVILEGED ACCESS ---\n\n"
        "<b>ADMIN PROTOCOLS ($ prefix):</b>\n"
        + "\n".join([f"• ${cmd}" for cmd in sorted(admin_protocols)]) + "\n\n"
        "<b>PUBLIC MODULES (/ prefix):</b>\n"
        + "\n".join([f"• /{cmd}" for cmd in sorted(public_modules)]) + "\n\n"
        "--- END OF INDEX ---"
    )

    await msg.reply_text(text, parse_mode="HTML")
