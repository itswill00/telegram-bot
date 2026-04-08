from telegram import Update
from telegram.ext import ContextTypes

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not user:
        return

    text = (
        "<b>COMMAND_LIST</b>\n\n"
        "<b>MEDIA_TOOLS</b>\n"
        "• <code>.dl [url]</code> - Media downloader\n"
        "• <code>.music [query]</code> - Audio search\n"
        "• <code>.kang</code> - Sticker tool\n\n"
        "<b>AI_MODELS</b>\n"
        "• <code>.ask [text]</code> - Gemini\n"
        "• <code>.groq [text]</code> - Groq\n\n"
        "<b>UTILITIES</b>\n"
        "• <code>.gsearch [query]</code> - Web search\n"
        "• <code>.weather [location]</code> - Weather\n"
        "• <code>.kurs [amount] [from] [to]</code> - Forex\n"
        "• <code>.tr [lang] [text]</code> - Translator\n"
        "• <code>.ship</code> - Interaction test\n"
        "• <code>.waifu</code> - Assets\n\n"
        "<b>SYSTEM_TOOLS</b>\n"
        "• <code>.ping</code> - Latency\n"
        "• <code>.stats</code> - System stats\n"
        "• <code>.ip [address]</code> - IP lookup\n"
        "• <code>.domain [url]</code> - Domain lookup\n"
        "• <code>.whoisdomain [url]</code> - WHOIS lookup\n\n"
        "<b>CONFIG</b>\n"
        "• <code>.settings</code> - User settings\n"
    )


    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

# The callback handler is kept purely empty but exported so that bot.py doesn't crash 
# if it maps help_callback in its routes.
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
