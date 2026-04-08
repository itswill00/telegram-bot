from telegram import Update
from telegram.ext import ContextTypes

from handlers.welcome import start_verify_pm

# start
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        arg = context.args[0]
        if arg.startswith("verify_"):
            return await start_verify_pm(update, context)
            
    user = update.effective_user
    name = (user.first_name or "").strip() or "Anonymous"
    text = (
        f"<b>SYSTEM DAEMON ONLINE</b>\n"
        f"• USER IDENTITY : <code>{name}</code>\n"
        f"• REGISTRY ID   : <code>{user.id}</code>\n"
        f"• STATUS        : <code>ACTIVE</code>\n\n"
        f"<i>Ketik /help untuk mengakses indeks utilitas publik bot ini.</i>"
    )
    await update.message.reply_text(text, parse_mode="HTML")