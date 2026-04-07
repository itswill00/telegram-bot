import os
import sqlite3
import time

DB_PATH = "data/system.sqlite3"

def _db():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

def init_system_db():
    con = _db()
    try:
        con.execute(
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
            con.execute(
                "INSERT OR IGNORE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, val, time.time())
            )
        con.commit()
    finally:
        con.close()

def get_setting(key: str, default: str = "OFF") -> str:
    con = _db()
    try:
        cur = con.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default
    finally:
        con.close()

def set_setting(key: str, value: str):
    con = _db()
    try:
        con.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value.upper(), time.time())
        )
        con.commit()
    finally:
        con.close()
