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
        "<b>CORE_ACCESS</b>\n"


        "<b>System </b>  —  Prefix: <code>$</code>\n"
        "• <code>$core</code>      : Buka panel admin\n"
        "• <code>$meter</code>     : Tampilkan metrik server\n"
        "• <code>$sh</code> / <code>$py</code> : Eksekusi shell / python\n"
        "• <code>$sync</code>      : Sinkronisasi git pull\n"
        "• <code>$reboot</code>    : Muat ulang daemon\n"
        "• <code>$live</code>      : Toggle live-reload\n"
        "• <code>$token</code>     : Perbarui token cookies\n"
        "• <code>$dump</code>      : Generate arsip ZIP\n"
        "• <code>$load</code>      : Restore DB via ZIP\n\n"

        "<b>Moderation </b>  —  Prefix: <code>$</code>\n"
        "• <code>$purge</code>     : Ban dari grup\n"
        "• <code>$revive</code>    : Cabut ban grup\n"
        "• <code>$hush</code>      : Restriksi chat\n"
        "• <code>$eject</code>      : Kick dari grup\n"
        "• <code>$grant</code>      : Berikan akses sudo\n"
        "• <code>$revoke</code>     : Cabut akses sudo\n"
        "• <code>$trusted</code>    : List user sudo\n"
        "• <code>$nodes</code>      : Identifikasi daftar grup\n"
        "• <code>$push</code>       : Transmisi pesan massal\n\n"

        "<b>Utilities </b>  —  Prefix: <code>.</code>\n"
        "• <code>.wlc</code>       : Konfigurasi welcome menu\n"
        "• <code>.autodl</code>    : Konfigurasi auto-download\n"
        "• <code>.ask</code>       : Query AI text\n"
        "• <code>.dl</code>        : Download media URL\n"
        "• <code>.weather</code>   : Pengesanan parameter cuaca\n"
        "• <code>.speedtest</code> : Pengujian bandwidth server\n"
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
