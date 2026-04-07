import os
import zipfile
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from utils.config import LOG_CHAT_ID

logger = logging.getLogger(__name__)

async def backup_database(context: ContextTypes.DEFAULT_TYPE):
    """
    Zips the 'data/' folder and sends it to the log chat.
    """
    if not LOG_CHAT_ID:
        logger.warning("LOG_CHAT_ID not set, skipping auto backup")
        return

    data_dir = "data"
    if not os.path.exists(data_dir):
        logger.warning(f"'{data_dir}' directory not found, nothing to backup")
        return

    zip_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    try:
        # Create zip in memory/temp file
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if not file.endswith('.tmp'): # Skip temporary files
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, data_dir))

        # Send to Telegram
        with open(zip_name, 'rb') as f:
            await context.bot.send_document(
                chat_id=LOG_CHAT_ID,
                document=f,
                caption=(
                    f"<b>Pencadangan Basis Data Otomatis</b>\n"
                    f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Lokasi: Seluruh berkas di direktori <code>data/</code>"
                ),
                parse_mode="HTML"
            )
        
        logger.info(f"✓ Auto backup sent to {LOG_CHAT_ID}")

    except Exception as e:
        logger.error(f"Failed to perform auto backup: {e}")
    finally:
        # Cleanup zip file
        if os.path.exists(zip_name):
            os.remove(zip_name)
