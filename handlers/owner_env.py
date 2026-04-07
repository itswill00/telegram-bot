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
        # Tampilkan daftar key yang ada
        if not os.path.exists(ENV_PATH):
            return await msg.reply_text("❌ <code>.env</code> file not found.", parse_mode="HTML")
        
        with open(ENV_PATH, "r") as f:
            lines = f.readlines()
        
        keys = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                keys.append(f"• <code>{key}</code>")
        
        text = (
            "⚙️ <b>Environment Variables</b>\n\n"
            + "\n".join(keys) + "\n\n"
            "<b>Usage:</b>\n"
            "• <code>$env GET KEY</code>\n"
            "• <code>$env SET KEY=VALUE</code>"
        )
        return await msg.reply_text(text, parse_mode="HTML")

    action = context.args[0].upper()

    if action == "GET" and len(context.args) > 1:
        key = context.args[1].strip()
        val = os.getenv(key)
        if val is None:
            return await msg.reply_text(f"❌ Key <code>{key}</code> not found.", parse_mode="HTML")
        
        return await msg.reply_text(
            f"🔑 <b>{key}</b>\n"
            f"<code>{html.escape(val)}</code>",
            parse_mode="HTML"
        )

    if action == "SET" and len(context.args) > 1:
        raw = " ".join(context.args[1:]).strip()
        if "=" not in raw:
            return await msg.reply_text("❌ Format must be <code>KEY=VALUE</code>", parse_mode="HTML")
        
        key, val = raw.split("=", 1)
        key = key.strip()
        val = val.strip()

        try:
            # Update file .env
            set_key(ENV_PATH, key, val)
            
            # Update os.environ (Hot Reload)
            os.environ[key] = val
            
            # Optional: Reload dotenv to be sure
            load_dotenv(ENV_PATH, override=True)

            return await msg.reply_text(
                f"✅ <b>Success!</b>\n"
                f"Key <code>{key}</code> has been updated.\n\n"
                "<i>Changes are applied immediately (Hot Reloaded).</i>",
                parse_mode="HTML"
            )
        except Exception as e:
            return await msg.reply_text(f"❌ <b>Error:</b>\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

    return await msg.reply_text("❌ Unknown action. Use <b>GET</b> or <b>SET</b>.", parse_mode="HTML")
