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
        "<code>────────────────────────────────────────</code>\n"
        "<i>Select a module below to view detailed specifications.</i>"
    ),

    "features": (
        "<b>[ SYSTEM FEATURES ]</b>\n"
        "<code>──────────────────────</code>\n"
        "• <code>/dl</code>        : Remote media download engine\n"
        "• <code>/weather</code>   : Meteorological data query\n"
        "• <code>/music</code>     : Audio repository search\n"
        "• <code>/gsearch</code>   : Web indexing service\n"
        "• <code>/tr</code>        : Translation dispatcher\n"
        "• <code>/trlist</code>    : Supported languages array\n"
        "• <code>/ship</code>      : Social compatibility analysis\n"
        "• <code>/reminder</code>  : Temporal notification scheduler\n"
        "• <code>/waifu</code>     : Graphical asset generator\n"
        "• <code>/kurs</code>      : Financial exchange rate engine\n"
        "• <code>/q</code>         : Dynamic quote converter\n"
        "• <code>/kang</code>      : Sticker pack synchronizer\n"
    ),

    "ai": (
        "<b>[ AI ENGINES ]</b>\n"
        "<code>──────────────────────</code>\n"
        "• <code>/ask</code>  : Google Gemini 2.0 Flash engine\n"
        "• <code>/groq</code> : Groq Llama-3 technical engine\n"
    ),

    "utils": (
        "<b>[ SYSTEM UTILITIES ]</b>\n"
        "<code>──────────────────────</code>\n"
        "• <code>/ping</code>        : Latency measurement\n"
        "• <code>/stats</code>       : Resource metrics\n"
        "• <code>/ip</code>          : IP metadata lookup\n"
        "• <code>/domain</code>      : Registry indexing\n"
        "• <code>/whoisdomain</code> : Extended WHOIS query\n"
    ),

    "privacy": (
        "<b>[ PRIVACY PROTOCOL ]</b>\n"
        "<code>──────────────────────</code>\n"
        "• <b>Collection:</b> Commands and timestamps logged for optimization.\n"
        "• <b>Usage:</b> Solely for technical maintenance.\n"
        "• <b>Security:</b> Avoid sending sensitive credentials.\n\n"
        "<i>Interaction constitutes full agreement to protocol.</i>"
    ),

    "settings": (
        "<b>[ SYSTEM CONFIGURATION ]</b>\n"
        "<code>───────────────────────────</code>\n"
        "<i>Select a configuration module below.</i>"
    ),

    "autodl": (
        "<b>[ AUTO DOWNLOAD PROTOCOL ]</b>\n"
        "<code>────────────────────────────</code>\n"
        "• <code>/autodl enable</code>  : Activate link detection\n"
        "• <code>/autodl disable</code> : Deactivate link detection\n"
        "• <code>/autodl status</code>  : View boolean state\n"
    ),

    "wlc": (
        "<b>[ WELCOME PROTOCOL ]</b>\n"
        "<code>──────────────────────</code>\n"
        "• <code>/wlc enable</code>  : Activate greeting routine\n"
        "• <code>/wlc disable</code> : Terminate greeting routine\n"
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
