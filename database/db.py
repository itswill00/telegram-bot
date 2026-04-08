import sqlite3
import os
import logging
import asyncio
import functools
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

log = logging.getLogger(__name__)

def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Creates a connection to the SQLite database with standard performance settings.
    Ensures the directory for db_path exists.
    """
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # Note: check_same_thread=False is needed if we yield the connection across threads in asyncio wrappers!
    con = sqlite3.connect(db_path, check_same_thread=False)
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
    except sqlite3.Error as e:
        log.warning(f"Failed to set PRAGMA for {db_path}: {e}")
    return con

@contextmanager
def db_session(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """
    Legacy synchronous Context manager for database connections.
    Closes the connection automatically.
    """
    con = get_connection(db_path)
    try:
        yield con
    finally:
        con.close()

# --- ENTERPRISE MATURITY ASYNC WRAPPER ---

@asynccontextmanager
async def db_session_async(db_path: str) -> AsyncGenerator[sqlite3.Connection, None]:
    """
    Asynchronous unblocking context manager for SQLite.
    Bridges synchronous sqlite3 connections into non-blocking asyncio thread pools.
    """
    loop = asyncio.get_running_loop()
    
    # Initialize connection in a background thread to prevent disk I/O blocking
    con = await loop.run_in_executor(None, get_connection, db_path)
    try:
        yield con
    finally:
        # Close connection asynchronously
        await loop.run_in_executor(None, con.close)

class AsyncDBWrapper:
    """
    Utility wrapper to execute connection methods via threadpool
    Instead of `con.execute(...)`, you pass your queries to an executor wrapper.
    Usage:
      async with db_session_async(path) as con:
         cursor = await execute_async(con, "SELECT * FROM x")
    """
    pass

async def execute_async(con: sqlite3.Connection, query: str, params: tuple = ()) -> sqlite3.Cursor:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, con.execute, query, params)

async def commit_async(con: sqlite3.Connection) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, con.commit)

