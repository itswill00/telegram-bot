from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from handlers.setting import render_settings_message


def _help_cb(user_id: int, action: str) -> str:
    return f"help:{int(user_id)}:{action}"


def help_main_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("SYSTEM FEATURES", callback_data=_help_cb(user_id, "features")),
            InlineKeyboardButton("AI ENGINES", callback_data=_help_cb(user_id, "ai")),
        ],
        [
            InlineKeyboardButton("UTILITIES", callback_data=_help_cb(user_id, "utils")),
            InlineKeyboardButton("PRIVACY POLICY", callback_data=_help_cb(user_id, "privacy")),
        ],
        [
            InlineKeyboardButton("GLOBAL SETTINGS", callback_data=_help_cb(user_id, "settings")),
        ],
        [
            InlineKeyboardButton("TERMINATE", callback_data=_help_cb(user_id, "close")),
        ],
    ])


def help_settings_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("AutoDL", callback_data=_help_cb(user_id, "autodl")),
            InlineKeyboardButton("Welcome", callback_data=_help_cb(user_id, "wlc")),
        ],
        [
            InlineKeyboardButton("User Settings", callback_data=_help_cb(user_id, "user_setting")),
        ],
        [
            InlineKeyboardButton("BACK", callback_data=_help_cb(user_id, "menu")),
            InlineKeyboardButton("TERMINATE", callback_data=_help_cb(user_id, "close")),
        ],
    ])


def help_back_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("BACK", callback_data=_help_cb(user_id, "menu"))],
        [InlineKeyboardButton("TERMINATE", callback_data=_help_cb(user_id, "close"))],
    ])


def help_settings_back_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("BACK", callback_data=_help_cb(user_id, "settings"))],
        [InlineKeyboardButton("TERMINATE", callback_data=_help_cb(user_id, "close"))],
    ])


HELP_TEXT = {
    "menu": (
        "<b>SYSTEM DOCUMENTATION</b>\n"
        "Select a module below to view detailed specifications."
    ),

    "features": (
        "<b>SYSTEM FEATURES</b>\n\n"
        "• /dl - Remote media download engine\n"
        "• /weather - Meteorological data query\n"
        "• /music - Audio repository search\n"
        "• /gsearch - Web indexing service\n"
        "• /tr - Multi-language translation engine\n"
        "• /trlist - Supported language specifications\n"
        "• /ship - Social compatibility analysis\n"
        "• /reminder - Temporal notification scheduler\n"
        "• /waifu - Graphical asset generator\n"
        "• /kurs - Financial exchange rate engine\n"
        "• /q - Dynamic quote-to-sticker converter\n"
        "• /kang - Sticker pack synchronization\n"
    ),

    "ai": (
        "<b>AI ENGINES</b>\n\n"
        "• /ask - Google Gemini 2.0 Flash engine\n"
        "• /groq - Groq Llama-3 technical engine\n"
    ),

    "utils": (
        "<b>SYSTEM UTILITIES</b>\n\n"
        "• /ping - Latency measurement\n"
        "• /stats - Resource utilization metrics\n"
        "• /ip - IP metadata lookup\n"
        "• /domain - Domain registry indexing\n"
        "• /whoisdomain - Extended WHOIS protocol query\n"
    ),

    "privacy": (
        "<b>PRIVACY PROTOCOL</b>\n\n"
        "User agreement and data handling specifications:\n\n"
        "• Data Collection: Commands, timestamps, and identifiers are logged for system optimization.\n"
        "• Usage: Information is utilized solely for maintenance and debugging.\n"
        "• Security: Avoid transmission of sensitive credentials or private keys.\n\n"
        "Continuing interaction constitutes full agreement to these terms."
    ),

    "settings": (
        "<b>SYSTEM CONFIGURATION</b>\n\n"
        "Select a configuration module below."
    ),

    "autodl": (
        "<b>Auto Download Protocol</b>\n\n"
        "• /autodl enable - Activate link detection\n"
        "• /autodl disable - Deactivate link detection\n"
        "• /autodl status - View current status\n\n"
    ),

    "wlc": (
        "<b>Welcome Protocol</b>\n\n"
        "• /wlc enable - Activate new member greeting\n"
        "• /wlc disable - Deactivate new member greeting\n\n"
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
            await q.answer("CRITICAL: Invalid help session.", show_alert=True)
        except Exception:
            pass
        return

    action = parts[2]

    if q.from_user.id != owner_id:
        try:
            await q.answer(
                "UNAUTHORIZED: Session restricted to initiator.",
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
