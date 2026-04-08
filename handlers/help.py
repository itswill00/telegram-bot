from telegram import Update
from telegram.ext import ContextTypes

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not user:
        return

    text = (
        "<b>Command Reference</b>\n\n"
        "<b>Data & Media Extraction</b>\n"
        "• <code>/dl [url]</code> - Media download execution\n"
        "• <code>/music [query]</code> - Audio asset fetching\n"
        "• <code>/kang</code> - Sticker synchronization\n\n"
        "<b>Artificial Intelligence</b>\n"
        "• <code>/ask [text]</code> - Gemini model inference\n"
        "• <code>/groq [text]</code> - Groq computational model\n\n"
        "<b>Utility & Analytics</b>\n"
        "• <code>/gsearch [query]</code> - Web search indexing\n"
        "• <code>/weather [location]</code> - Weather metrics\n"
        "• <code>/kurs [jumlah] [asal] [tujuan]</code> - Forex index\n"
        "• <code>/tr [lang] [text]</code> - Text translation\n"
        "• <code>/ship</code> - Compatibility testing\n"
        "• <code>/waifu</code> - Character asset lookup\n\n"
        "<b>System Diagnostics</b>\n"
        "• <code>/ping</code> - Latency calculation\n"
        "• <code>/stats</code> - Hardware telemetry\n"
        "• <code>/ip [address]</code> - IP lookup\n"
        "• <code>/domain [url]</code> - DNS registry\n"
        "• <code>/whoisdomain [url]</code> - WHOIS extraction\n\n"
        "<b>Configuration</b>\n"
        "• <code>/settings</code> - Parameter configuration\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

# The callback handler is kept purely empty but exported so that bot.py doesn't crash 
# if it maps help_callback in its routes.
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
