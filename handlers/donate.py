from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.config import DONATE_URL


async def donate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if not DONATE_URL:
        return await msg.reply_text(
            "<b>ERROR:</b> DONATE_LINK_UNDEFINED",
            parse_mode="HTML"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("DONATE_VIA_QRIS", url=DONATE_URL)]
    ])

    text = (
        "<b>DONATION_PORTAL</b>\n\n"
        "Direct contribution link below. Post-transaction, send a manual notification to the @HirohitoKiyoshi to synchronize premium status."
    )


    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=kb,
        disable_web_page_preview=True,
    )