from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from handlers.setting import render_settings_message


def _help_cb(user_id: int, action: str) -> str:
    return f"help:{int(user_id)}:{action}"


def help_main_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Features", callback_data=_help_cb(user_id, "features")),
            InlineKeyboardButton("AI Chat", callback_data=_help_cb(user_id, "ai")),
        ],
        [
            InlineKeyboardButton("Utilities", callback_data=_help_cb(user_id, "utils")),
            InlineKeyboardButton("Privacy", callback_data=_help_cb(user_id, "privacy")),
        ],
        [
            InlineKeyboardButton("Settings", callback_data=_help_cb(user_id, "settings")),
        ],
        [
            InlineKeyboardButton("Close", callback_data=_help_cb(user_id, "close")),
        ],
    ])


def help_settings_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("AutoDL", callback_data=_help_cb(user_id, "autodl")),
            InlineKeyboardButton("Welcome", callback_data=_help_cb(user_id, "wlc")),
        ],
        [
            InlineKeyboardButton("User Setting", callback_data=_help_cb(user_id, "user_setting")),
        ],
        [
            InlineKeyboardButton("Back", callback_data=_help_cb(user_id, "menu")),
            InlineKeyboardButton("Close", callback_data=_help_cb(user_id, "close")),
        ],
    ])


def help_back_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=_help_cb(user_id, "menu"))],
        [InlineKeyboardButton("Close", callback_data=_help_cb(user_id, "close"))],
    ])


def help_settings_back_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=_help_cb(user_id, "settings"))],
        [InlineKeyboardButton("Close", callback_data=_help_cb(user_id, "close"))],
    ])


HELP_TEXT = {
    "menu": (
        "📖 <b>Help Menu</b>\n"
        "Select a category to see available commands."
    ),

    "features": (
        "<b>Main Features</b>\n\n"
        "• <code>/dl</code> — Download videos from supported platforms\n"
        "• <code>/weather</code> — Get weather information\n"
        "• <code>/music</code> — Search music\n"
        "• <code>/gsearch</code> — Search on Google\n"
        "• <code>/tr</code> — Translate text between languages\n"
        "• <code>/trlist</code> — List supported languages\n"
        "• <code>/ship</code> — Choose a couple\n"
        "• <code>/reminder</code> — Schedule a reminder\n"
        "• <code>/waifu</code> — Get a waifu\n"
        "• <code>/kurs</code> — Currency conversion\n"
        "• <code>/q</code> — Create quote sticker\n"
        "• <code>/kang</code> — Add sticker to your pack\n"
    ),

    "ai": (
        "<b>AI Chat</b>\n\n"
        "• <code>/ask</code> — Chat with Gemini AI\n"
        "• <code>/groq</code> — Chat with Groq AI\n"
    ),

    "utils": (
        "<b>Utilities</b>\n\n"
        "• <code>/ping</code> — Check bot response time\n"
        "• <code>/stats</code> — Bot & system statistics\n"
        "• <code>/ip</code> — IP address lookup\n"
        "• <code>/domain</code> — Domain information\n"
        "• <code>/whoisdomain</code> — Detailed domain lookup\n"
    ),

    "privacy": (
        "<b>User Privacy</b>\n\n"
        "By using this bot, you understand and agree that:\n\n"
        "• The bot owner may view and store command history\n"
        "• Recorded data may include:\n"
        "  - Telegram user ID\n"
        "  - Username (if available)\n"
        "  - Commands used\n"
        "  - Timestamp\n\n"
        "This data is only used for:\n"
        "• Development & Maintenance\n"
        "• Service improvement\n\n"
        "<b>❗ Do not send passwords or other sensitive data.</b>\n\n"
        "By using this bot, you are considered to have agreed to this policy."
    ),

    "settings": (
        "<b>Bot Settings</b>\n\n"
        "Select a category below to see detailed options."
    ),

    "autodl": (
        "<b>Auto Download Link</b>\n\n"
        "• <code>/autodl enable</code> — Enable automatic link detection\n"
        "• <code>/autodl disable</code> — Disable automatic link detection\n"
        "• <code>/autodl status</code> — Check status\n\n"
    ),

    "wlc": (
        "<b>Welcome Settings</b>\n\n"
        "• <code>/wlc enable</code> — Enable welcome messages\n"
        "• <code>/wlc disable</code> — Disable welcome messages\n\n"
    ),
}


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not user:
        return

    await update.message.reply_text(
        HELP_TEXT["menu"],
        reply_markup=help_main_keyboard(user.id),
        parse_mode="HTML"
    )


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q or not q.data:
        return

    parts = q.data.split(":", 2)
    if len(parts) != 3 or parts[0] != "help":
        return

    try:
        owner_id = int(parts[1])
    except Exception:
        try:
            await q.answer("Invalid help menu.", show_alert=True)
        except Exception:
            pass
        return

    action = parts[2]

    if q.from_user.id != owner_id:
        try:
            await q.answer(
                "Only the user who opened this menu can access it",
                show_alert=True
            )
        except Exception:
            pass
        return

    try:
        await q.answer()
    except Exception:
        pass

    if action == "close":
        try:
            await q.message.delete()
        except Exception:
            pass
        return

    if action == "menu":
        await q.edit_message_text(
            HELP_TEXT["menu"],
            reply_markup=help_main_keyboard(owner_id),
            parse_mode="HTML"
        )
        return

    if action == "settings":
        await q.edit_message_text(
            HELP_TEXT["settings"],
            reply_markup=help_settings_keyboard(owner_id),
            parse_mode="HTML"
        )
        return

    if action == "user_setting":
        return await render_settings_message(q.message, owner_id, source="help")

    text = HELP_TEXT.get(action)
    if text:
        if action in ("autodl", "wlc"):
            kb = help_settings_back_keyboard(owner_id)
        else:
            kb = help_back_keyboard(owner_id)

        await q.edit_message_text(
            text,
            reply_markup=kb,
            parse_mode="HTML"
        )
