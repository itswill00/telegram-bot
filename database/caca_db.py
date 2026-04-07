import os
import time
import json
import asyncio
from typing import Dict, Set, Any, Optional

CACA_JSON_PATH = "data/caca_db.json"

_MODE_CACHE: Dict[int, str] = {}
_GROUPS_CACHE: Set[int] = set()
_APPROVED_CACHE: Set[int] = set()
_lock = asyncio.Lock()

def _load_db() -> Dict[str, Any]:
    if not os.path.exists(CACA_JSON_PATH):
        return {"modes": {}, "groups": [], "approved": []}
    try:
        with open(CACA_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure proper types
            if "modes" not in data: data["modes"] = {}
            if "groups" not in data: data["groups"] = []
            if "approved" not in data: data["approved"] = []
            return data
    except (json.JSONDecodeError, IOError):
        return {"modes": {}, "groups": [], "approved": []}

def _save_db(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(CACA_JSON_PATH), exist_ok=True)
    temp_path = f"{CACA_JSON_PATH}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, CACA_JSON_PATH)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

async def init():
    global _MODE_CACHE, _GROUPS_CACHE, _APPROVED_CACHE
    async with _lock:
        data = await asyncio.to_thread(_load_db)
        _MODE_CACHE = {int(k): str(v) for k, v in data.get("modes", {}).items()}
        _GROUPS_CACHE = {int(gid) for gid in data.get("groups", [])}
        _APPROVED_CACHE = {int(uid) for uid in data.get("approved", [])}

def get_mode(user_id: int) -> str:
    return _MODE_CACHE.get(int(user_id), "default")

async def set_mode(user_id: int, mode: str):
    async with _lock:
        _MODE_CACHE[int(user_id)] = str(mode)
        data = await asyncio.to_thread(_load_db)
        data["modes"] = {str(k): v for k, v in _MODE_CACHE.items()}
        await asyncio.to_thread(_save_db, data)

async def remove_mode(user_id: int):
    async with _lock:
        if int(user_id) in _MODE_CACHE:
            del _MODE_CACHE[int(user_id)]
            data = await asyncio.to_thread(_load_db)
            data["modes"] = {str(k): v for k, v in _MODE_CACHE.items()}
            await asyncio.to_thread(_save_db, data)

async def load_groups() -> Set[int]:
    return _GROUPS_CACHE

async def add_group(chat_id: int):
    async with _lock:
        _GROUPS_CACHE.add(int(chat_id))
        data = await asyncio.to_thread(_load_db)
        data["groups"] = list(_GROUPS_CACHE)
        await asyncio.to_thread(_save_db, data)

async def remove_group(chat_id: int):
    async with _lock:
        if int(chat_id) in _GROUPS_CACHE:
            _GROUPS_CACHE.remove(int(chat_id))
            data = await asyncio.to_thread(_load_db)
            data["groups"] = list(_GROUPS_CACHE)
            await asyncio.to_thread(_save_db, data)

async def save_groups(groups: Set[int]):
    global _GROUPS_CACHE
    async with _lock:
        _GROUPS_CACHE = set(groups)
        data = await asyncio.to_thread(_load_db)
        data["groups"] = list(_GROUPS_CACHE)
        await asyncio.to_thread(_save_db, data)