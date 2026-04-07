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
        "<b>SYSTEM ADMIN INDEX</b>\n"
        "<code>────────────────────────────────────────</code>\n"
        "<i>Owner Privileged Dashboard & Command Guide</i>\n\n"

        "<b>[ SYSTEM & SERVER ]</b>  —  Prefix: <code>$</code>\n"
        "• <code>$admin</code>     — Buka Panel Dashboard Utama\n"
        "• <code>$stats</code>     — Cek Info Eksekusi (RAM/CPU/Net)\n"
        "• <code>$sh</code> / <code>eval</code> — Eksekusi Shell/Bash / Python\n"
        "• <code>$update</code>    — Git Pull & Pembaruan Sistem\n"
        "• <code>$restart</code>   — Muat Ulang Proses (Reboot)\n"
        "• <code>$hotreload</code> — Togel mode pengawasan koding\n"
        "• <code>$cookies</code>   — Konfigurasi ulang token YT/IG\n"
        "• <code>$backup</code>    — Buat dan unduh arsip data ZIP\n"
        "• <code>$restore</code>   — (Reply ZIP) Pulihkan Database\n\n"

        "<b>[ CONTROL & ACCESS ]</b>  —  Prefix: <code>$</code>\n"
        "• <code>$ban</code>       — Keluarkan + Cegah gabung grup\n"
        "• <code>$unban</code>     — Buka penangguhan blokir grup\n"
        "• <code>$mute</code>      — Hapus hak kirim pesan anggota\n"
        "• <code>$kick</code>      — Keluarkan tanpa cegah gabung\n"
        "• <code>$banuser</code>   — Blokir akses bot secara global\n"
        "• <code>$addsudo</code>   — Rekrut izin level administrator\n"
        "• <code>$sudolist</code>  — Pantau register Sudo aktif\n"
        "• <code>$groups</code>    — Index tabel grup naungan\n"
        "• <code>$broadcast</code> — Transmisi pengumuman massal\n\n"

        "<b>[ UTILITIES (PUBLIC) ]</b>  —  Prefix: <code>/</code>\n"
        "• <code>/wlc</code>       — Konfigurator gerbang Sambutan\n"
        "• <code>/autodl</code>    — Konfigurator pendeteksi Tautan\n"
        "• <code>/ask</code>       — Kognisi LLM (Gemini 2.0)\n"
        "• <code>/dl</code>        — Akuisisi berkas Media Sosial\n"
        "• <code>/weather</code>   — Laporan Cuaca Global\n"
        "• <code>/speedtest</code> — Uji Kecepatan Uplink/Downlink\n"
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
