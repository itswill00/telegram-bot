import time
from database.db import db_session_async, DB_PATH

async def init_system_db():
    async with db_session_async(DB_PATH) as con:
        await con.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        # Default values
        defaults = [
            ("auto_backup", "ON"),
            ("maintenance_mode", "OFF"),
            ("ai_global", "ON")
        ]
        for key, val in defaults:
            await con.execute(
                "INSERT OR IGNORE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, val, time.time())
            )

async def get_setting(key: str, default: str = "OFF") -> str:
    async with db_session_async(DB_PATH) as con:
        cur = await con.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else default

async def set_setting(key: str, value: str):
    async with db_session_async(DB_PATH) as con:
        await con.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value.upper(), time.time())
        )

