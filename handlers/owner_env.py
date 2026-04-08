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
            return await msg.reply_text("STATUS: ENV MISSING", parse_mode="HTML")
        
        with open(ENV_PATH, "r") as f:
            lines = f.readlines()
        
        keys = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                keys.append(f"• {key}")
        
        text = (
            "<b>ENV CONFIG</b>\n\n"
            + "\n".join(keys) + "\n\n"
            "<b>OPERATIONS:</b>\n"
            "• $env GET &lt;KEY&gt;\n"
            "• $env SET &lt;KEY&gt;=&lt;VAL&gt;\n"
            "• $env PULL\n"
            "• $env PUSH (Reply with file)"
        )
        return await msg.reply_text(text, parse_mode="HTML")

    action = context.args[0].upper()

    if action == "PULL":
        if not os.path.exists(ENV_PATH):
            return await msg.reply_text("ERROR: ENV MISSING")
        
        try:
            with open(ENV_PATH, "rb") as f:
                await context.bot.send_document(
                    chat_id=msg.chat_id,
                    document=f,
                    filename=".env",
                    caption="<b>ENV BACKUP</b>"
                )
        except Exception:
            await msg.reply_text("ERROR: SEND FAILED")
        return

    if action == "PUSH":
        if not msg.reply_to_message or not msg.reply_to_message.document:
            return await msg.reply_text("ERROR: DOCUMENT REQUIRED")
        
        status_msg = await msg.reply_text("EXECUTING...")
        try:
            doc = msg.reply_to_message.document
            new_file = await context.bot.get_file(doc.file_id)
            await new_file.download_to_drive(ENV_PATH)
            load_dotenv(ENV_PATH, override=True)
            await status_msg.edit_text("SUCCESS: ENV OVERWRITTEN")
            await asyncio.sleep(2)
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"ERROR: {html.escape(str(e))}")
        return

    if action == "GET" and len(context.args) > 1:
        key = context.args[1].strip()
        val = os.getenv(key)
        if val is None:
            return await msg.reply_text(f"ERROR: KEY UNDEFINED ({key})", parse_mode="HTML")
        
        return await msg.reply_text(
            f"KEY: {key}\n"
            f"VAL: <code>{html.escape(val)}</code>",
            parse_mode="HTML"
        )

    if action == "SET" and len(context.args) > 1:
        raw = " ".join(context.args[1:]).strip()
        if "=" not in raw:
            return await msg.reply_text("ERROR: INVALID SYNTAX (KEY=VALUE)", parse_mode="HTML")
        
        key, val = raw.split("=", 1)
        key = key.strip()
        val = val.strip()

        try:
            set_key(ENV_PATH, key, val)
            os.environ[key] = val
            load_dotenv(ENV_PATH, override=True)

            res_msg = await msg.reply_text(
                f"SUCCESS: CONFIG UPDATED\n"
                f"KEY: {key}\n"
                "STATUS: RELOADED",
                parse_mode="HTML"
            )
            await asyncio.sleep(2)
            await res_msg.delete()
        except Exception as e:
            await msg.reply_text(f"ERROR: {html.escape(str(e))}", parse_mode="HTML")
        return

    return await msg.reply_text("ERROR: UNKNOWN ACTION", parse_mode="HTML")


