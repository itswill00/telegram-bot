import time
from telegram import Update
from telegram.ext import ContextTypes

#ping
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.perf_counter()
    msg = await update.message.reply_text("Probing...")
    end = time.perf_counter()
    latency = int((end - start) * 1000)
    await msg.edit_text(
        f"<b>CONNECTION STATUS</b>\n"
        f"• LATENCY: <code>{latency} ms</code>",
        parse_mode="HTML"
    )
