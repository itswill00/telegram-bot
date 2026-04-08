import os
import time
from utils.config import OWNER_ID
from database.premium import is_premium
from handlers.dl.constants import AUTO_DL_DB
from database.db import db_session_async

async def init_auto_dl_db():
    async with db_session_async(AUTO_DL_DB) as con:
        await con.execute(
            """
            CREATE TABLE IF NOT EXISTS auto_dl_groups (
                chat_id INTEGER PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 1,
                updated_at REAL NOT NULL
            )
            """
        )

async def load_auto_dl() -> set[int]:
    async with db_session_async(AUTO_DL_DB) as con:
        cur = await con.execute("SELECT chat_id FROM auto_dl_groups WHERE enabled=1")
        rows = await cur.fetchall()
        return {int(r[0]) for r in rows if r and r[0] is not None}

async def save_auto_dl(groups: set[int]):
    async with db_session_async(AUTO_DL_DB) as con:
        now = time.time()
        await con.execute("UPDATE auto_dl_groups SET enabled=0, updated_at=?", (float(now),))
        if groups:
            await con.executemany(
                """
                INSERT INTO auto_dl_groups (chat_id, enabled, updated_at)
                VALUES (?, 1, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                  enabled=1,
                  updated_at=excluded.updated_at
                """,
                [(int(cid), float(now)) for cid in groups],
            )

def extract_domain(url: str) -> str:
    import re
    u = (url or "").strip().lower()
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    m = re.search(r"https?://([^/]+)", u)
    if not m:
        return ""
    host = m.group(1)
    host = host.split(":", 1)[0]
    return host

def is_premium_required(url: str, premium_domains: set[str]) -> bool:
    host = extract_domain(url)
    if not host:
        return False
    for d in premium_domains:
        d = d.lower()
        if host == d or host.endswith("." + d):
            return True
    return False

def is_premium_user(user_id: int) -> bool:
    uid = int(user_id)
    if uid in OWNER_ID:
        return True
    return is_premium(uid)