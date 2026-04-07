import os
import random
import sqlite3
import time

from telegram import Update
from telegram.ext import ContextTypes

from database.ship_db import (
    get_users_pool,
    set_ship_last_time,
    get_ship_last_time,
    add_user,
    _ship_db_init,
)

SHIP_COOLDOWN = 60 * 60 * 24

SHIP_MESSAGES = [
    "Compatibility score indicates high synchronization potential.",
    "Data analysis suggests a stable and understanding dynamic.",
    "Interaction patterns reflect natural synergy.",
    "Subconscious alignment detected between subjects.",
    "Collaboration between these profiles appears optimal.",
    "Security and trust metrics are within the upper percentiles.",
    "Communication flow is predicted to be seamless.",
    "Thermal energy metrics suggest a warm interaction.",
    "A simple yet profound connection is evidenced.",
    "Mutual support protocols are active."
]

SHIP_ENDING = [
    "Analysis completed.",
    "Prediction based on current metrics.",
    "Synchronized.",
    "Protocol active.",
    "End of report.",
]

def tag(u):
    return f'<a href="tg://user?id={u["id"]}">{u["name"]}</a>'

async def _is_chat_member(bot, chat_id: int, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status not in ("left", "kicked")
    except Exception:
        return False
        
def format_remaining(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

async def ship_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return

    now = int(time.time())
    last_time = get_ship_last_time(chat.id)

    if now - last_time < SHIP_COOLDOWN:
        remain = SHIP_COOLDOWN - (now - last_time)
        return await msg.reply_text(
            f"<b>COOLDOWN ACTIVE</b>\n\n"
            f"Next analysis available in:\n"
            f"<code>{format_remaining(remain)}</code>",
            parse_mode="HTML",
        )

    add_user(chat.id, msg.from_user)
    pool = get_users_pool(chat.id)

    if len(pool) < 2:
        return await msg.reply_text("<b>ERROR:</b> Insufficient data pool for analysis.")

    pool_ids = [p for p in pool if p.get("id") is not None]
    picked = random.sample(pool_ids, 2)
    u1, u2 = picked[0], picked[1]

    percent = random.randint(50, 100)
    msg_text = random.choice(SHIP_MESSAGES)
    ending = random.choice(SHIP_ENDING)

    text = (
        f"<b>COMPATIBILITY ANALYSIS REPORT</b>\n\n"
        f"SUBJECT A: {tag(u1)}\n"
        f"SUBJECT B: {tag(u2)}\n\n"
        f"SYNC RATE: <code>{percent}%</code>\n\n"
        f"METRICS: {msg_text}\n"
        f"<i>{ending}</i>"
    )

    await msg.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)
    set_ship_last_time(chat.id, now)

try:
    _ship_db_init()
except Exception:
    pass
