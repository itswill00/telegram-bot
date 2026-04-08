from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.config import DONATE_URL


async def donate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if not DONATE_URL:
        return await msg.reply_text(
            "<b>ERROR:</b> DONATE LINK UNDEFINED",
            parse_mode="HTML"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("PORTAL", url=DONATE_URL)]
    ])

    text = (
        "<b>DONATION PORTAL</b>\n\n"
        "Direct contribution link below. Post-transaction, notify @HirohitoKiyoshi to verify premium status."
    )


    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=kb,
        disable_web_page_preview=True,
    )