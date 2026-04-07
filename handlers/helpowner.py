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
        "👑 <b>OWNER DASHBOARD & COMMAND INDEX</b>\n"
        "<i>Panduan lengkap seluruh instruksi sistem.</i>\n\n"

        "💻 <b>1. KONTROL SISTEM (Prefix <code>$</code>)</b>\n"
        "• <code>$admin</code> - Buka Panel Dashboard Utama\n"
        "• <code>$sys</code> / <code>$stats</code> - Cek Info Server (RAM/CPU)\n"
        "• <code>$eval</code> / <code>$sh</code> - Eksekusi skrip / Bash Terminal\n"
        "• <code>$env</code> - Cek environment variables\n"
        "• <code>$update</code> - Tarik kode Github & Update bot\n"
        "• <code>$restart</code> - Mulai ulang proses bot\n"
        "• <code>$hotreload</code> - Aktifkan mode auto-restart dev\n"
        "• <code>$cookies</code> - Perbarui akses kuki (cookies) IG/YT\n"
        "• <code>$backup</code> - Buat dan unduh arsip data ZIP\n"
        "• <code>$restore</code> - (Reply ZIP) Pulihkan data & restart\n\n"

        "🛡 <b>2. MODERASI & AKSES (Prefix <code>$</code>)</b>\n"
        "• <code>$ban</code> / <code>$unban</code> - Banned/Unban di dalam grup\n"
        "• <code>$mute</code> / <code>$unmute</code> - Bungkam anggota grup\n"
        "• <code>$kick</code> - Keluarkan anggota dari grup\n"
        "• <code>$banuser</code> / <code>$unbanuser</code> - Banned akses bot global\n"
        "• <code>$addsudo</code> / <code>$rmsudo</code> - Beri/Cabut akses Sudo\n"
        "• <code>$sudolist</code> - Lihat daftar Sudo terdaftar\n"
        "• <code>$groups</code> - Lihat grup bot bergabung\n"
        "• <code>$broadcast</code> - Kirim pesan massal ke pengguna\n\n"

        "🌐 <b>3. UTILTITAS GRUP & GLOBAL (Prefix <code>/</code>)</b>\n"
        "• <code>/wlc</code> - Buka menu pengaturan Sambutan & Captcha\n"
        "• <code>/autodl</code> - Buka menu deteksi tautan Media\n"
        "• <code>/settings</code> - Menu pengaturan privat pengguna\n"
        "• <code>/premium</code> - Kelola / Klaim akses premium\n\n"

        "🤖 <b>4. MODUL MESIN PUBLIK (Prefix <code>/</code>)</b>\n"
        "• <code>/dl</code> - Unduh konten media (TikTok, IG, YT, dll)\n"
        "• <code>/ask</code> - Analisis teks pintar menggunakan Gemini 2.0\n"
        "• <code>/groq</code> - Mesin pencarian teks teknis LLaMA-3\n"
        "• <code>/music</code> - Pencari lagu dari repositori\n"
        "• <code>/gsearch</code> - Mesin pencari situs Web\n"
        "• <code>/weather</code> - Pantau cuaca dan iklim\n"
        "• <code>/speedtest</code> - Uji kecepatan jaringan internet\n"
        "• <code>/ping</code> - Uji latensi waktu sistem\n"
        "• <code>/whoisdomain</code> / <code>/domain</code> / <code>/ip</code> - Analisis jaringan\n"
        "• <code>/tr</code> / <code>/trlist</code> - Mesin terjemahan multi-bahasa\n"
        "• <code>/waifu</code> - Generator grafis gambar anime 2D\n"
        "• ... serta puluhan utilitas mini (/q, /ship, /reminder) yang dapat dilihat pengguna melalui /help\n"
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
