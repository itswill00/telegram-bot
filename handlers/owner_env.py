import os
import html
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv, set_key

from utils.config import OWNER_ID

ENV_PATH = ".env"
logger = logging.getLogger(__name__)

async def env_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if not msg or not user or user.id not in OWNER_ID:
        return

    if not context.args:
        if not os.path.exists(ENV_PATH):
            return await msg.reply_text("STATUS: .env file not found.", parse_mode="HTML")
        
        with open(ENV_PATH, "r") as f:
            lines = f.readlines()
        
        keys = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                keys.append(f"- {key}")
        
        text = (
            "<b>ENVIRONMENT CONFIGURATION</b>\n\n"
            + "\n".join(keys) + "\n\n"
            "<b>PROTOCOLS:</b>\n"
            "• $env GET &lt;KEY&gt;\n"
            "• $env SET &lt;KEY&gt;=&lt;VALUE&gt;\n"
            "• $env PULL (Download file)\n"
            "• $env PUSH (Reply to a .env file)"
        )
        return await msg.reply_text(text, parse_mode="HTML")

    action = context.args[0].upper()

    if action == "PULL":
        if not os.path.exists(ENV_PATH):
            return await msg.reply_text("ERROR: .env file missing.")
        
        status_msg = await msg.reply_text("INITIALIZING: Transmission of configuration file...")
        try:
            with open(ENV_PATH, "rb") as f:
                await context.bot.send_document(
                    chat_id=msg.chat_id,
                    document=f,
                    filename=".env",
                    caption="<b>CONFIDENTIAL:</b> Current Environment Configuration."
                )
            await status_msg.delete()
        except Exception:
            await status_msg.edit_text("ERROR: Transmission failed.")
        return

    if action == "PUSH":
        if not msg.reply_to_message or not msg.reply_to_message.document:
            return await msg.reply_text("ERROR: Target document required.")
        
        status_msg = await msg.reply_text("INITIALIZING: Configuration overwrite sequence...")
        try:
            doc = msg.reply_to_message.document
            new_file = await context.bot.get_file(doc.file_id)
            await new_file.download_to_drive(ENV_PATH)
            load_dotenv(ENV_PATH, override=True)
            await status_msg.edit_text("SUCCESS: Configuration overwritten and hot-reloaded.")
            await asyncio.sleep(5)
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"CRITICAL ERROR: {html.escape(str(e))}")
        return

    if action == "GET" and len(context.args) > 1:
        key = context.args[1].strip()
        val = os.getenv(key)
        if val is None:
            return await msg.reply_text(f"ERROR: Key {key} undefined.", parse_mode="HTML")
        
        return await msg.reply_text(
            f"IDENT: {key}\n"
            f"VALUE: <code>{html.escape(val)}</code>",
            parse_mode="HTML"
        )

    if action == "SET" and len(context.args) > 1:
        raw = " ".join(context.args[1:]).strip()
        if "=" not in raw:
            return await msg.reply_text("ERROR: Malformed syntax. Use KEY=VALUE.", parse_mode="HTML")
        
        key, val = raw.split("=", 1)
        key = key.strip()
        val = val.strip()

        try:
            set_key(ENV_PATH, key, val)
            os.environ[key] = val
            load_dotenv(ENV_PATH, override=True)

            res_msg = await msg.reply_text(
                f"SUCCESS: Configuration updated.\n"
                f"KEY: {key}\n"
                "STATUS: Hot-reload completed.",
                parse_mode="HTML"
            )
            await asyncio.sleep(5)
            await res_msg.delete()
        except Exception as e:
            await msg.reply_text(f"CRITICAL ERROR: {html.escape(str(e))}", parse_mode="HTML")
        return

    return await msg.reply_text("ERROR: Unknown action protocol.", parse_mode="HTML")
