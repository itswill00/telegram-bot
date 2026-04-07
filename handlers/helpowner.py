from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from utils.config import OWNER_ID


def helpowner_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Close", callback_data="helpowner:close")]
    ])


async def helpowner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if user.id not in OWNER_ID:
        return

    text = (
        "<b>Owner Commands</b>\n"
        "<i>Administrative & system-level controls</i>\n\n"

        "<b>System Management</b>\n"
        "• <code>/update</code> — Update system Bot.\n"
        "• <code>/speedtest</code> — Run server speed test.\n"
        "• <code>/broadcast</code> — Announcement.\n"
        "• <code>/wlc</code> — Configure welcome message.\n"
        "• <code>/restart</code> — Restart the bot.\n\n"

        "<b>Access & Billing</b>\n"
        "• <code>/cookies</code> — Update cookies via Telegram.\n"
        "• <code>/premium</code> — Manage premium users.\n\n"
        "<b>Moderation Tools</b>\n"
        "• <code>/ban</code> — Ban a user.\n"
        "• <code>/unban</code> — Unban a user.\n"
        "• <code>/sudolist</code> — List sudo users.\n"
    )

    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=helpowner_keyboard()
    )


async def helpowner_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    if q.data != "helpowner:close":
        return

    try:
        await q.message.delete()
    except Exception:
        pass
