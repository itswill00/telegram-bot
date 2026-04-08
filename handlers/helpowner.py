import html
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from utils.config import OWNER_ID

def helpowner_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tutup Menu", callback_data="helpowner:close")]
    ])

async def helpowner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if not user or user.id not in OWNER_ID:
        return

    text = (
        "<b>SYSTEM COMMAND INDEX</b>\n"

        "<b>System </b>  —  Prefix: <code>$</code>\n"
        "• <code>$admin</code>     : Buka panel admin\n"
        "• <code>$stats</code>     : Tampilkan metrik server\n"
        "• <code>$sh</code> / <code>eval</code> : Eksekusi shell / python\n"
        "• <code>$update</code>    : Sinkronisasi git pull\n"
        "• <code>$restart</code>   : Muat ulang daemon\n"
        "• <code>$hotreload</code> : Toggle live-reload\n"
        "• <code>$cookies</code>   : Perbarui token cookies\n"
        "• <code>$backup</code>    : Generate arsip ZIP\n"
        "• <code>$restore</code>   : Restore DB via ZIP\n\n"

        "<b>Moderation </b>  —  Prefix: <code>$</code>\n"
        "• <code>$ban</code>       : Ban dari grup\n"
        "• <code>$unban</code>     : Cabut ban grup\n"
        "• <code>$mute</code>      : Restriksi chat\n"
        "• <code>$kick</code>      : Kick dari grup\n"
        "• <code>$banuser</code>   : Ban dari bot (global)\n"
        "• <code>$addsudo</code>   : Berikan akses sudo\n"
        "• <code>$sudolist</code>  : List user sudo\n"
        "• <code>$groups</code>    : Identifikasi daftar grup\n"
        "• <code>$broadcast</code> : Transmisi pesan massal\n\n"

        "<b>Utilities </b>  —  Prefix: <code>/</code>\n"
        "• <code>/wlc</code>       : Konfigurasi welcome menu\n"
        "• <code>/autodl</code>    : Konfigurasi auto-download\n"
        "• <code>/ask</code>       : Query AI text\n"
        "• <code>/dl</code>        : Download media URL\n"
        "• <code>/weather</code>   : Pengesanan parameter cuaca\n"
        "• <code>/speedtest</code> : Pengujian bandwidth server\n"
    )

    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=helpowner_keyboard()
    )

async def helpowner_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    if q.data != "helpowner:close":
        return

    try:
        await q.message.delete()
    except Exception:
        pass
