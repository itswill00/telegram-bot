import os
import time
import json
import asyncio
from typing import Dict, Any, List, Optional

MEMORY_EXPIRE = 60 * 60 * 24
JSON_PATH = "data/caca_memory.json"
META_MAX_TURNS = 20

# Memory cache to reduce disk I/O
_cache: Dict[str, Dict[str, Any]] = {}
_lock = asyncio.Lock()

def _load_json() -> Dict[str, Any]:
    if not os.path.exists(JSON_PATH):
        return {}
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_json(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    temp_path = f"{JSON_PATH}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # Atomic rename for data safety
        os.replace(temp_path, JSON_PATH)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

async def init():
    global _cache
    async with _lock:
        _cache = await asyncio.to_thread(_load_json)

async def get_history(user_id: int) -> List[Dict[str, str]]:
    uid = str(user_id)
    async with _lock:
        data = _cache.get(uid)
        if not data:
            return []
        return data.get("history", [])

async def set_history(user_id: int, history: List[Dict[str, str]], last_message_id: Optional[int] = None):
    uid = str(user_id)
    # Enforce history limit
    if META_MAX_TURNS > 0:
        max_msgs = META_MAX_TURNS * 2
        if len(history) > max_msgs:
            history = history[-max_msgs:]

    async with _lock:
        if uid not in _cache:
            _cache[uid] = {}
        
        _cache[uid]["history"] = history
        _cache[uid]["last_used"] = time.time()
        if last_message_id is not None:
            _cache[uid]["last_message_id"] = last_message_id
            
        await asyncio.to_thread(_save_json, _cache)

async def set_last_message_id(user_id: int, last_message_id: Optional[int]):
    uid = str(user_id)
    async with _lock:
        if uid not in _cache:
            _cache[uid] = {"history": [], "last_used": time.time()}
        
        _cache[uid]["last_message_id"] = last_message_id
        _cache[uid]["last_used"] = time.time()
        await asyncio.to_thread(_save_json, _cache)

async def get_last_message_id(user_id: int) -> Optional[int]:
    uid = str(user_id)
    async with _lock:
        data = _cache.get(uid)
        if not data:
            return None
        return data.get("last_message_id")

async def clear(user_id: int):
    uid = str(user_id)
    async with _lock:
        if uid in _cache:
            del _cache[uid]
            await asyncio.to_thread(_save_json, _cache)

async def cleanup():
    cutoff = time.time() - MEMORY_EXPIRE
    async with _lock:
        to_delete = [
            uid for uid, val in _cache.items() 
            if val.get("last_used", 0) < cutoff
        ]
        if to_delete:
            for uid in to_delete:
                del _cache[uid]
            await asyncio.to_thread(_save_json, _cache)

async def has_last_message_id(message_id: int) -> bool:
    async with _lock:
        for val in _cache.values():
            if val.get("last_message_id") == message_id:
                return True
        return False