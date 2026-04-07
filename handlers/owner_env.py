import os
import html
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv, set_key

from utils.config import OWNER_ID

ENV_PATH = ".env"

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
            "<b>COMMANDS:</b>\n"
            "• $env GET &lt;KEY&gt;\n"
            "• $env SET &lt;KEY&gt;=&lt;VALUE&gt;"
        )
        return await msg.reply_text(text, parse_mode="HTML")

    action = context.args[0].upper()

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

            return await msg.reply_text(
                f"SUCCESS: Configuration updated.\n"
                f"KEY: {key}\n"
                "STATUS: Hot-reload completed.",
                parse_mode="HTML"
            )
        except Exception as e:
            return await msg.reply_text(f"CRITICAL ERROR: {html.escape(str(e))}", parse_mode="HTML")

    return await msg.reply_text("ERROR: Unknown action protocol.", parse_mode="HTML")
