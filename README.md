# telebot

Asisten Telegram profesional berperforma tinggi yang dioptimalkan khusus untuk lingkungan **Android/Termux**. Bot ini dirancang dengan fokus pada efisiensi, keamanan data lokal, dan manajemen jarak jauh tanpa gimik.

## Karakteristik Utama

- **Optimasi Termux:** Pemantauan sistem asli (CPU, RAM, Disk) tanpa ketergantungan pada library berat seperti `psutil`.
- **Database Lokal Aman:** Menggunakan sistem penyimpanan JSON Atomic (thread-safe) untuk menjamin integritas data meskipun terjadi pemutusan daya mendadak.
- **Manajemen Jarak Jauh:** Panel admin interaktif dan alat pengembang langsung dari Telegram.
- **Infrastruktur Async:** Dibangun di atas `python-telegram-bot` v22.6+ untuk penanganan permintaan konkuren yang cepat.
- **Tanpa Gimik:** Antarmuka bersih, tanpa emoji berlebihan, dan respon profesional yang lugas.

## Fitur Unggulan

- **Asisten AI (Caca):** Didukung oleh Groq (Llama 3/Moonshot) dengan kepribadian profesional dan informatif.
- **Dashboard Admin ($admin):** Pantau statistik sistem, log, dan lakukan pencadangan data melalui tombol interaktif.
- **Pencadangan Otomatis:** Seluruh direktori `data/` dipadatkan (ZIP) dan dikirim ke chat log setiap 12 jam.
- **Pelaporan Galat Global:** Traceback kesalahan sistem dikirim secara instan ke pemilik untuk perbaikan cepat.
- **Owner Tools:** Eksekusi kode Python ($eval) dengan format In/Out dan perintah shell ($sh) langsung dari chat.
- **Keamanan:** Daftar hitam global (Global Blacklist) untuk membatasi akses pengguna yang tidak diinginkan.

## Struktur Perintah

| Jenis | Prefix | Deskripsi |
| :--- | :--- | :--- |
| **Publik** | `/` | Perintah umum seperti `/start`, `/ask`, `/dl`, `/music`, `/tr`. |
| **Admin** | `$` | Perintah operasional seperti `$admin`, `$eval`, `$sh`, `$banuser`, `$stats`. |

## Instalasi di Termux

1. **Perbarui Paket:**
   ```bash
   pkg update && pkg upgrade
   pkg install python ndk-sysroot clang make binutils ffmpeg tesseract libjpeg-turbo libpng libxml2 libxslt
   ```

2. **Klon Repositori:**
   ```bash
   git clone <repository_url> telebot
   cd telebot
   ```

3. **Instal Dependensi Python:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment:**
   Edit berkas `.env` dan lengkapi kredensial Anda:
   ```bash
   nano .env
   ```

## Konfigurasi .env

| Variabel | Keterangan |
| :--- | :--- |
| `BOT_TOKEN` | Token dari @BotFather. |
| `OWNER_ID` | ID Telegram pemilik (Pisahkan dengan koma jika lebih dari satu). |
| `LOG_CHAT_ID` | ID grup/chat untuk log error dan backup data. |
| `GROQ_API_KEY` | Kunci API dari console.groq.com. |
| `GEMINI_API_KEY` | Kunci API dari Google AI Studio. |

## Menjalankan Bot

Untuk menjalankan bot beserta server lokal Telegram Bot API:
```bash
python main.py
```
Atau jalankan bot saja:
```bash
python bot.py
```

## Keamanan & Privasi

Semua data tersimpan secara lokal di direktori `data/` dalam format JSON yang dapat dibaca manusia. Tidak ada data yang dikirim ke server pihak ketiga selain penyedia API AI yang Anda gunakan.

---
**Pengembang:** noticesa
**Lisensi:** GPL-3.0
