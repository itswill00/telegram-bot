import os
import time
import asyncio
import aiosqlite
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

BROADCAST_DB = "data/broadcast.sqlite3"

# In-memory deduplication sets to minimize disk I/O
_SEEN_USERS = set()
_SEEN_GROUPS = set()
_USERNAME_CACHE = {}  # {user_id: (username, last_updated)}

# Lock for initialization
_INIT_LOCK = asyncio.Lock()
_DB_READY = False

async def _db_init():
    global _DB_READY
    async with _INIT_LOCK:
        if _DB_READY:
            return
        os.makedirs("data", exist_ok=True)
        async with aiosqlite.connect(BROADCAST_DB) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS broadcast_users (
                    chat_id INTEGER PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS broadcast_groups (
                    chat_id INTEGER PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS broadcast_user_cache (
                    username TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    updated_at REAL NOT NULL
                );
            """)
            await db.commit()
        
        # Pre-load existing IDs into memory to avoid redundant inserts
        async with aiosqlite.connect(BROADCAST_DB) as db:
            async with db.execute("SELECT chat_id FROM broadcast_users") as cursor:
                async for row in cursor:
                    _SEEN_USERS.add(row[0])
            async with db.execute("SELECT chat_id FROM broadcast_groups") as cursor:
                async for row in cursor:
                    _SEEN_GROUPS.add(row[0])
                    
        _DB_READY = True

async def _add_user(chat_id: int):
    if chat_id in _SEEN_USERS:
        return
    
    if not _DB_READY: await _db_init()
    
    try:
        async with aiosqlite.connect(BROADCAST_DB) as db:
            now = time.time()
            await db.execute("""
                INSERT INTO broadcast_users (chat_id, enabled, updated_at)
                VALUES (?, 1, ?)
                ON CONFLICT(chat_id) DO UPDATE SET enabled=1, updated_at=excluded.updated_at
            """, (int(chat_id), float(now)))
            await db.commit()
            _SEEN_USERS.add(chat_id)
    except Exception as e:
        logger.error(f"Collector Error (User): {e}")

async def _add_group(chat_id: int):
    if chat_id in _SEEN_GROUPS:
        return

    if not _DB_READY: await _db_init()

    try:
        async with aiosqlite.connect(BROADCAST_DB) as db:
            now = time.time()
            await db.execute("""
                INSERT INTO broadcast_groups (chat_id, enabled, updated_at)
                VALUES (?, 1, ?)
                ON CONFLICT(chat_id) DO UPDATE SET enabled=1, updated_at=excluded.updated_at
            """, (int(chat_id), float(now)))
            await db.commit()
            _SEEN_GROUPS.add(chat_id)
    except Exception as e:
        logger.error(f"Collector Error (Group): {e}")

async def cache_username(user_id: int, username: str | None):
    u = (username or "").strip().lstrip("@").lower()
    if not u:
        return

    now = time.time()
    # Throttling updates to once per 24 hours per user
    cached = _USERNAME_CACHE.get(user_id)
    if cached and cached[0] == u and (now - cached[1]) < 86400:
        return

    if not _DB_READY: await _db_init()

    try:
        async with aiosqlite.connect(BROADCAST_DB) as db:
            await db.execute("""
                INSERT INTO broadcast_user_cache (username, user_id, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET user_id=excluded.user_id, updated_at=excluded.updated_at
            """, (u, int(user_id), float(now)))
            await db.commit()
            _USERNAME_CACHE[user_id] = (u, now)
    except Exception as e:
        logger.error(f"Collector Error (Username): {e}")

async def collect_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous shard for collecting networking nodes."""
    chat = update.effective_chat
    if not chat:
        return

    if chat.type == "private":
        await _add_user(chat.id)
    else:
        await _add_group(chat.id)

    u = update.effective_user
    if u and getattr(u, "id", None):
        await cache_username(int(u.id), getattr(u, "username", None))

    msg = update.message
    if msg and msg.reply_to_message and msg.reply_to_message.from_user:
        ru = msg.reply_to_message.from_user
        await cache_username(int(ru.id), getattr(ru, "username", None))