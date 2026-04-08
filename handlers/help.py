from telegram import Update
from telegram.ext import ContextTypes

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not user:
        return

    text = (
        "<b>COMMAND LIST</b>\n"
        "Interface control manual:\n\n"
        "<b>MEDIA TOOLS</b>\n"
        "• <code>.dl [url]</code> - Media acquisition\n"
        "• <code>.music [query]</code> - Audio stream search\n"
        "• <code>.kang</code> - Sticker porting tool\n\n"
        "<b>AI MODELS</b>\n"
        "• <code>.ask [text]</code> - Gemini interface\n"
        "• <code>.groq [text]</code> - Groq interface\n\n"
        "<b>UTILITIES</b>\n"
        "• <code>.gsearch [query]</code> - Web search engine\n"
        "• <code>.weather [city]</code> - Meteorological report\n"
        "• <code>.kurs [n] [f] [t]</code> - Currency exchange\n"
        "• <code>.tr [lang] [text]</code> - Translation utility\n"
        "• <code>.ship</code> - Proximity analysis\n"
        "• <code>.waifu</code> - Asset generation\n\n"
        "<b>SYSTEM METRICS</b>\n"
        "• <code>.ping</code> - Network latency probe\n"
        "• <code>.stats</code> - Hardware diagnostics\n"
        "• <code>.ip [addr]</code> - Geo-IP lookup\n"
        "• <code>.domain [url]</code> - Domain query\n\n"
        "<b>CONFIGURATION</b>\n"
        "• <code>.settings</code> - Local parameter control\n"
    )


    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

# The callback handler is kept purely empty but exported so that bot.py doesn't crash 
# if it maps help_callback in its routes.
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
