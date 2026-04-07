#!/usr/bin/env python3

import os
import socket
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, JobQueue, ContextTypes

from utils.http import close_http_session
from handlers.commands import register_commands
from handlers.callbacks import register_callbacks
from handlers.messages import register_messages
from utils.startup import startup_tasks
from utils.config import BOT_TOKEN, LOG_CHAT_ID
from utils.backup import backup_database
from database.system_db import get_setting, init_system_db

BOT_USERNAME = None

LOCAL_BOT_API_HOST = os.getenv("LOCAL_BOT_API_HOST", "127.0.0.1")
LOCAL_BOT_API_PORT = int(os.getenv("LOCAL_BOT_API_PORT", "8081"))
PREFER_LOCAL_BOT_API = os.getenv("PREFER_LOCAL_BOT_API", "1").strip().lower() not in ("0", "false", "no")


class EmojiFormatter(logging.Formatter):
    EMOJI = {
        logging.INFO: "➜",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "💥",
    }

    def format(self, record):
        emoji = self.EMOJI.get(record.levelno, "•")
        record.msg = f"{emoji} {record.msg}"
        return super().format(record)


def setup_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(
        EmojiFormatter("[%(asctime)s] %(message)s", "%H:%M:%S")
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)


log = logging.getLogger(__name__)


def _local_bot_api_available(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _build_application():
    builder = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .job_queue(JobQueue())
        .concurrent_updates(True)
        .connect_timeout(30)
        .read_timeout(60 * 20)
        .write_timeout(60 * 20)
        .pool_timeout(60)
    )

    if PREFER_LOCAL_BOT_API and _local_bot_api_available(LOCAL_BOT_API_HOST, LOCAL_BOT_API_PORT):
        base = f"http://{LOCAL_BOT_API_HOST}:{LOCAL_BOT_API_PORT}"
        log.info(f"✓ Using local Telegram Bot API at {base}")
        builder = (
            builder
            .base_url(f"{base}/bot")
            .base_file_url(f"{base}/file/bot")
        )
    else:
        if PREFER_LOCAL_BOT_API:
            log.warning("Local Telegram Bot API unavailable, falling back to official Telegram Bot API")
        else:
            log.info("✓ Local Telegram Bot API disabled, using official Telegram Bot API")

    return builder.build()


async def post_init(app):
    global BOT_USERNAME

    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        log.warning(f"Failed to clear webhook/pending updates: {e}")

    try:
        me = await app.bot.get_me()
        BOT_USERNAME = (me.username or "").lower()
        if BOT_USERNAME:
            log.info(f"✓ Bot username loaded: @{BOT_USERNAME}")
        else:
            log.info("✓ Bot username loaded")
    except Exception as e:
        log.warning(f"Failed to get bot username: {e}")

    try:
        await app.bot.set_my_commands([
            ("start", "Check bot status"),
            ("donate", "Support bot development"),
            ("help", "Show help menu"),
            ("settings", "User settings"),
            ("quiz", "Random quiz"),
            ("ping", "Check latency"),
            ("ship", "Choose a couple"),
            ("stats", "System statistics"),
            ("dl", "Download video"),
            ("ask", "Ask Gemini AI"),
            ("music", "Search music"),
            ("groq", "Ask Groq AI"),
            ("gsearch", "Google search"),
            ("tr", "Translate text"),
        ])
        log.info("✓ Bot commands set")
    except Exception as e:
        log.warning(f"Failed to set bot commands: {e}")

    try:
        cmds = await app.bot.get_my_commands()
        app.bot_data["commands"] = cmds
        log.info("✓ Cached bot commands: " + ", ".join(c.command for c in cmds))
    except Exception as e:
        log.warning(f"Failed to cache bot commands: {e}")

    # Initialize System Settings
    try:
        init_system_db()
        log.info("✓ System settings database initialized")
    except Exception as e:
        log.warning(f"Failed to initialize system settings: {e}")

    # Auto backup based on setting
    if app.job_queue and get_setting("auto_backup", "ON") == "ON":
        app.job_queue.run_repeating(
            backup_database, 
            interval=60 * 60 * 12, # 12 hours
            first=10, # run first backup 10 seconds after startup
            name="auto_backup"
        )
        log.info("✓ Auto backup job scheduled (12h)")
    else:
        log.info("✓ Auto backup job is disabled (OFF)")

    await startup_tasks(app)
    log.info("✓ Startup tasks executed")


async def post_shutdown(app):
    await close_http_session()
    log.info("HTTP session closed")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    log.error("Exception while handling an update:", exc_info=context.error)

    if not LOG_CHAT_ID:
        return

    import traceback
    import html

    # traceback.format_exception returns a list of strings
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message
    message = (
        f"<b>Error Terdeteksi pada Sistem Bot</b>\n"
        f"Tipe: {type(context.error).__name__}\n"
        f"Pesan: {html.escape(str(context.error))}\n\n"
        f"<b>Traceback:</b>\n"
        f"<pre>{html.escape(tb_string[-3500:])}</pre>" 
    )

    try:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Failed to send error report to Telegram: {e}")


def main():
    setup_logger()
    log.info("Initializing bot")

    app = _build_application()

    app.post_init = post_init
    app.post_shutdown = post_shutdown
    app.add_error_handler(error_handler)

    register_commands(app)
    register_messages(app)
    register_callbacks(app)

    log.info("--- SYSTEM INITIALIZED ---")
    log.info("Handlers registered successfully")
    log.info("Service: Polling active")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
