import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

ANALYTICS_PATH = "data/analytics.json"
_lock = asyncio.Lock()

def _load_stats() -> Dict[str, Any]:
    if not os.path.exists(ANALYTICS_PATH):
        return {"total_commands": 0, "users": {}, "commands": {}}
    try:
        with open(ANALYTICS_PATH, "r") as f:
            return json.load(f)
    except:
        return {"total_commands": 0, "users": {}, "commands": {}}

def _save_stats(data: Dict[str, Any]):
    os.makedirs("data", exist_ok=True)
    with open(ANALYTICS_PATH, "w") as f:
        json.dump(data, f)

async def track_command(user_id: int, command: str):
    async with _lock:
        data = await asyncio.to_thread(_load_stats)
        
        data["total_commands"] += 1
        
        uid = str(user_id)
        if uid not in data["users"]:
            data["users"][uid] = 0
        data["users"][uid] += 1
        
        if command not in data["commands"]:
            data["commands"][command] = 0
        data["commands"][command] += 1
        
        await asyncio.to_thread(_save_stats, data)

async def get_stats() -> Dict[str, Any]:
    async with _lock:
        return await asyncio.to_thread(_load_stats)
