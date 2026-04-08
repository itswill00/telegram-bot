import json
from typing import List, Dict, Any
from database.db import db_session_async

DB_PATH = "data/ai_memory.db"

async def init_ai_memory_db():
    async with db_session_async(DB_PATH) as con:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS ai_memory (
                user_id INTEGER PRIMARY KEY,
                engine TEXT,
                history_json TEXT
            )
        """)

async def get_ai_history(user_id: int, engine: str = "groq") -> List[Dict[str, Any]]:
    """Retrieve chat history for a specific AI engine."""
    async with db_session_async(DB_PATH) as con:
        cur = await con.execute("SELECT history_json FROM ai_memory WHERE user_id = ? AND engine = ?", (user_id, engine))
        row = await cur.fetchone()
        if row and row[0]:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return []
        return []

async def save_ai_history(user_id: int, history: List[Dict[str, Any]], engine: str = "groq") -> None:
    """Save chat history for a specific AI engine. Cap history length at 30 items to save space."""
    # Keep only the last 30 messages (15 interactions) to prevent huge DB bloat over time.
    if len(history) > 30:
        history = history[-30:]
        
    history_str = json.dumps(history)
    async with db_session_async(DB_PATH) as con:
        await con.execute("""
            INSERT INTO ai_memory (user_id, engine, history_json)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET history_json=excluded.history_json
        """, (user_id, engine, history_str))

async def clear_ai_history(user_id: int, engine: str = "groq") -> None:
    """Clear chat history for a specific user."""
    async with db_session_async(DB_PATH) as con:
        await con.execute("DELETE FROM ai_memory WHERE user_id = ? AND engine = ?", (user_id, engine))

