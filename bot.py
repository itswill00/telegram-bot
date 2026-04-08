#!/usr/bin/env python3

import os
import socket
import logging
import asyncio
import json

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
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
from database.ai_memory_db import init_ai_memory_db
from database.download_db import init_auto_dl_db

BOT_USERNAME = None

LOCAL_BOT_API_HOST = os.getenv("LOCAL_BOT_API_HOST", "127.0.0.1")
LOCAL_BOT_API_PORT = int(os.getenv("LOCAL_BOT_API_PORT", "8081"))
PREFER_LOCAL_BOT_API = os.getenv("PREFER_LOCAL_BOT_API", "1").strip().lower() not in ("0", "false", "no")


class TechnicalFormatter(logging.Formatter):
    LEVEL_PREFIX = {
        logging.INFO: "[INFO]",
        logging.WARNING: "[WARN]",
        logging.ERROR: "[ERR ]",
        logging.CRITICAL: "[CRIT]",
    }

    def format(self, record):
        prefix = self.LEVEL_PREFIX.get(record.levelno, "[LOG ]")
        record.msg = f"{prefix} {record.msg}"
        return super().format(record)


def setup_logger():
    # Stream Handler
    s_handler = logging.StreamHandler()
    s_handler.setFormatter(
        TechnicalFormatter("%(asctime)s %(message)s", "%H:%M:%S")
    )

    # File Handler for remote diagnostics
    f_handler = logging.FileHandler("bot.log", encoding='utf-8')
    f_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(s_handler)
    root.addHandler(f_handler)


    # Set specific level for our bot logger
    log.setLevel(logging.INFO)



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
        .connect_timeout(10)
        .read_timeout(10)
        .write_timeout(10)
        .pool_timeout(5)
    )

    if PREFER_LOCAL_BOT_API and _local_bot_api_available(LOCAL_BOT_API_HOST, LOCAL_BOT_API_PORT):
        base = f"http://{LOCAL_BOT_API_HOST}:{LOCAL_BOT_API_PORT}"
        log.info(f"Using local Telegram Bot API at {base}")
        builder = (
            builder
            .base_url(f"{base}/bot")
            .base_file_url(f"{base}/file/bot")
        )
    else:
        if PREFER_LOCAL_BOT_API:
            log.warning("Local Telegram Bot API unavailable, using remote endpoint")
        else:
            log.info("Local Telegram Bot API disabled, using remote endpoint")

    return builder.build()


async def post_init(app):
    global BOT_USERNAME

    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        log.warning(f"Failed to clear webhook: {e}")

    try:
        me = await app.bot.get_me()
        BOT_USERNAME = (me.username or "").lower()
        log.info(f"Identity loaded: @{BOT_USERNAME}" if BOT_USERNAME else "Identity loaded")
    except Exception as e:
        log.warning(f"Failed to load identity: {e}")

    try:
        await app.bot.set_my_commands([
            ("start", "Initialize bot session (.)"),
            ("help", "Access command documentation (.)"),
            ("settings", "Configure user preferences (.)"),
            ("quiz", "Execute technical assessment (.)"),
            ("ping", "Measure network latency (.)"),
            ("ship", "Run compatibility analysis (.)"),
            ("stats", "View system metrics (.)"),
            ("dl", "Process media download (.)"),
            ("ask", "Query AI engine (.)"),
            ("groq", "Query technical reasoning (.)"),
            ("gsearch", "Execute web search (.)"),
            ("tr", "Execute text translation (.)"),
        ])
        log.info("Global command set synchronized (Prefix: '.')")
    except Exception as e:
        log.warning(f"Failed to synchronize commands: {e}")


    try:
        cmds = await app.bot.get_my_commands()
        app.bot_data["commands"] = cmds
    except Exception:
        pass

    # Initialize System Settings
    try:
        await init_system_db()
        await init_ai_memory_db()
        await init_auto_dl_db()
        log.info("System configuration database initialized")
    except Exception as e:

        log.warning(f"Configuration initialization error: {e}")


    # Check for restart notification
    if os.path.exists("data/restart.json"):
        try:
            with open("data/restart.json", "r") as f:
                data = json.load(f)
            os.remove("data/restart.json")
            
            chat_id = data.get("chat_id")
            msg_id = data.get("msg_id")
            if chat_id:
                try:
                    import socket
                    host = socket.gethostname()
                    text = (
                        "<b>REBOOT SEQUENCE COMPLETE</b>\n"
                        "<code>"
                        f"STATUS : ACTIVE\n"
                        f"NODE   : {host}\n"
                        f"STATE  : OPERATIONAL"
                        "</code>"
                    )

                    await app.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_to_message_id=msg_id,
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

        except Exception as e:
            log.warning(f"Failed to send restart notification: {e}")

    # Auto backup based on setting
    if app.job_queue and (await get_setting("auto_backup", "ON")) == "ON":
        app.job_queue.run_repeating(
            backup_database, 
            interval=60 * 60 * 12,
            first=10,
            name="auto_backup"
        )

        log.info("Automated backup routine scheduled (12h cycle)")
    else:
        log.info("Automated backup routine is currently suspended")

    await startup_tasks(app)
    log.info("Boot sequence completed successfully")


async def post_shutdown(app):
    await close_http_session()
    log.info("HTTP session pool terminated")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Exception during update processing:", exc_info=context.error)

    if not LOG_CHAT_ID:
        return

    import traceback
    import html

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    message = (
        f"<b>CRITICAL SYSTEM ERROR</b>\n"
        f"TYPE: {type(context.error).__name__}\n"
        f"DESC: {html.escape(str(context.error))}\n\n"
        f"<b>TRACEBACK:</b>\n"
        f"<pre>{html.escape(tb_string[-3500:])}</pre>" 
    )

    try:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
    except Exception:
        pass


def main():
    setup_logger()
    log.info("Initializing system kernel")

    app = _build_application()

    app.post_init = post_init
    app.post_shutdown = post_shutdown
    app.add_error_handler(error_handler)

    register_commands(app)
    register_messages(app)
    register_callbacks(app)

    log.info("--- SYSTEM ONLINE ---")
    log.info("Polling service active")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
