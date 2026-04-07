import os
import zipfile
import logging
from datetime import datetime
from telegram.ext import ContextTypes

from utils.config import LOG_CHAT_ID

logger = logging.getLogger(__name__)

async def perform_backup(bot, target_chat_id: int):
    """
    Core logic to compress data directory and transmit via Telegram.
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        logger.warning("DATA_DIR_MISSING: Backup sequence aborted.")
        return False

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f"DB_SNAPSHOT_{timestamp}.zip"
    
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if not file.endswith(('.tmp', '.sqlite3-journal', '.sqlite3-wal')):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, data_dir))

        with open(zip_name, 'rb') as f:
            await bot.send_document(
                chat_id=target_chat_id,
                document=f,
                caption=(
                    f"<b>DATABASE SNAPSHOT REPORT</b>\n"
                    f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"SCOPE: /data/*\n"
                    f"STATUS: COMPLETED"
                ),
                parse_mode="HTML"
            )
        return True

    except Exception as e:
        logger.error(f"BACKUP_FAILURE: {e}")
        return False
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)

async def backup_database(context: ContextTypes.DEFAULT_TYPE):
    """
    Scheduled task wrapper.
    """
    if not LOG_CHAT_ID:
        return
    await perform_backup(context.bot, LOG_CHAT_ID)
