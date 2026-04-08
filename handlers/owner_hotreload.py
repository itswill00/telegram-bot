import os
import sys
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from utils.config import OWNER_ID

HOTRELOAD_TASK = None
WATCHED_MTIMES = {}

def get_py_mtimes(root_dir="."):
    """Returns a dict mapping file paths to their modification times for all .py files."""
    mtimes = {}
    for root, dirs, files in os.walk(root_dir):
        if "venv" in root or ".git" in root or "__pycache__" in root or "node_modules" in root:
            continue
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                try:
                    mtimes[path] = os.path.getmtime(path)
                except OSError:
                    pass
    return mtimes

async def watcher_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    global WATCHED_MTIMES
    WATCHED_MTIMES = get_py_mtimes()
    
    while True:
        await asyncio.sleep(2)
        current_mtimes = get_py_mtimes()
        
        for path, new_mtime in current_mtimes.items():
            old_mtime = WATCHED_MTIMES.get(path)
            # Compare if the file already existed and was modified
            if old_mtime is not None and new_mtime > old_mtime:
                file_name = os.path.basename(path)
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"<b>REBOOT TRIGGERED</b>\n\nSOURCE: <code>{file_name}</code>\nREBOOTING...",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                
                # Execv replacement to restart properly
                sys.stdout.flush()
                sys.stderr.flush()
                await asyncio.sleep(1)
                os.execv(sys.executable, [sys.executable] + sys.argv)
                
        # Keep track of newly created files or deleted ones
        WATCHED_MTIMES = current_mtimes

async def hotreload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global HOTRELOAD_TASK
    user = update.effective_user
    if not user or user.id not in OWNER_ID:
        return
        
    if HOTRELOAD_TASK and not HOTRELOAD_TASK.done():
        HOTRELOAD_TASK.cancel()
        HOTRELOAD_TASK = None
        await update.message.reply_text("<b>WATCHDOG TERMINATED</b>", parse_mode="HTML")
    else:
        HOTRELOAD_TASK = context.application.create_task(watcher_loop(context, update.message.chat_id))
        await update.message.reply_text("<b>WATCHDOG ACTIVE</b>\nNode will auto-reboot on source modification.", parse_mode="HTML")


