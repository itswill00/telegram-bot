import os
import logging
import asyncio
import aiosqlite
from contextlib import asynccontextmanager
from typing import AsyncGenerator

log = logging.getLogger(__name__)

async def get_connection(db_path: str) -> aiosqlite.Connection:
    """
    Creates an asynchronous connection to the SQLite database.
    """
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    con = await aiosqlite.connect(db_path)
    try:
        await con.execute("PRAGMA journal_mode=WAL;")
        await con.execute("PRAGMA synchronous=NORMAL;")
    except Exception as e:
        log.warning(f"Failed to set PRAGMA for {db_path}: {e}")
    return con

@asynccontextmanager
async def db_session_async(db_path: str) -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Native asynchronous context manager for SQLite using aiosqlite.
    """
    con = await get_connection(db_path)
    try:
        yield con
        await con.commit()
    finally:
        await con.close()
