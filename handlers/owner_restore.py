import os
import sys
import shutil
import zipfile
import html
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from utils.config import OWNER_ID

async def restore_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if not msg or not user or user.id not in OWNER_ID:
        return

    # User must reply to a zip file document
    if not msg.reply_to_message or not msg.reply_to_message.document:
        await msg.reply_text("<b>ERROR:</b> Silakan balas (_reply_) pada pesan backup ZIP untuk melakukan pengembalian data.", parse_mode="HTML")
        return

    doc = msg.reply_to_message.document
    if not doc.file_name.endswith('.zip'):
        await msg.reply_text("<b>ERROR:</b> Dokumen yang dibalas haruslah ber-ekstensi <code>.zip</code>.", parse_mode="HTML")
        return

    # Temporary messages
    status_msg = await msg.reply_text("<b>INITIALIZING:</b> Memulai proses unduhan file ZIP...", parse_mode="HTML")

    try:
        # Download ZIP
        file = await context.bot.get_file(doc.file_id)
        temp_zip = f"RESTORE_TMP_{doc.file_unique_id}.zip"
        await file.download_to_drive(temp_zip)

        await status_msg.edit_text("<b>SAFEGUARD:</b> Mengamankan direktori aktif ke dalam <code>data_backup/</code>...", parse_mode="HTML")

        # Basic Safeguard: Copy active data/ to data_backup/ if needed
        data_dir = "data"
        backup_dir = "data_backup"

        if os.path.exists(data_dir):
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir, ignore_errors=True)
            shutil.copytree(data_dir, backup_dir)
        else:
            os.makedirs(data_dir, exist_ok=True)

        await status_msg.edit_text("<b>EXTRACTION:</b> Mengurai (*unzip*) kedalam direktori <code>data/</code>...", parse_mode="HTML")

        # Extract Zip contents purely into data/
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            # zip_ref.extractall maintains the relative structure, backup.py saved it natively
            # so extracting it inside data/ will correctly put everything where it belongs.
            zip_ref.extractall(data_dir)

        # Clean temp zip
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

        await status_msg.edit_text("<b>REBOOTING:</b> Pemulihan selesai. Memicu bot _restart_ sistem...", parse_mode="HTML")

        # Trigger restart, exactly like restart_cmd
        sys.stdout.flush()
        sys.stderr.flush()
        
        # We add a slight sleep to let Telegram send the successful message above
        await asyncio.sleep(1)
        
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        await status_msg.edit_text(f"<b>CRITICAL ERROR:</b> Kegagalan _restore_.\n<pre>{html.escape(str(e))}</pre>", parse_mode="HTML")
        # Clean tmp zip on fail
        if 'temp_zip' in locals() and os.path.exists(temp_zip):
            os.remove(temp_zip)
