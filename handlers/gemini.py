import asyncio
import json
import html
from typing import Optional

import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from utils.system_prompt import split_message, sanitize_ai_output
from utils.config import GEMINI_API_KEY
from utils.http import get_http_session

from rag.retriever import retrieve_context
from rag.loader import load_local_contexts

from .groq import ask_groq_text

LOCAL_CONTEXTS = load_local_contexts()

from database.ai_memory_db import get_ai_history, save_ai_history, clear_ai_history

_AI_ACTIVE_USERS = {}


async def _typing_loop(bot, chat_id, stop: asyncio.Event):
    try:
        while not stop.is_set():
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)
    except Exception:
        pass


def _is_gemini_quota_error(status: Optional[int], text: str) -> bool:
    blob = f"{status or ''} {text or ''}".lower()
    keys = ["429", "quota", "resource_exhausted", "rate limit", "too many requests"]
    return any(k in blob for k in keys)


def _ai_history_to_groq(history: list) -> list:
    out = []
    for item in history:
        user_text = (item or {}).get("user")
        ai_text = (item or {}).get("ai")
        if user_text: out.append({"role": "user", "content": user_text})
        if ai_text: out.append({"role": "assistant", "content": ai_text})
    return out

_LOCAL_CONTEXTS = None

async def _get_local_contexts():
    global _LOCAL_CONTEXTS
    if _LOCAL_CONTEXTS is None:
        try:
            _LOCAL_CONTEXTS = load_local_contexts()
        except Exception:
            _LOCAL_CONTEXTS = []
    return _LOCAL_CONTEXTS

async def build_ai_prompt(user_id: int, user_prompt: str) -> str:
    history = await get_ai_history(user_id, "gemini")
    lines = []
    
    # Add history
    for h in history:
        lines.append(f"U: {h.get('user', '')}")
        lines.append(f"A: {h.get('ai', '')}")

    # Add RAG context lazily
    try:
        docs = await _get_local_contexts()
        if docs:
            contexts = await retrieve_context(user_prompt, docs, top_k=3)
            if contexts:
                lines.append("\n--- CONTEXT DATA ---")
                lines.extend(contexts)
                lines.append("--- END CONTEXT ---\n")
    except Exception:
        pass

    lines.append(f"U: {user_prompt}")
    return "\n".join(lines)


async def ask_ai_gemini(
    prompt: str,
    model: str = "gemini-2.0-flash",
) -> tuple[bool, str, Optional[int]]:
    if not GEMINI_API_KEY:
        return False, "API key missing.", None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": (
                        "IDENT: Axon\n"
                        "ARCH: @HirohitoKiyoshi\n"
                        "TONE: Professional Technical\n"
                        "EMOJI: FORBIDDEN\n"
                        "LOGIC: Automatic language detection. Formal Indonesian or Technical English."
                    )
                }
            ]
        },
        "tools": [{"google_search": {}}],
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
    }

    try:
        session = await get_http_session()
        async with session.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            if resp.status != 200:
                raw_text = await resp.text()
                return False, raw_text, resp.status
            data = await resp.json()

        candidates = data.get("candidates") or []
        if not candidates:
            return True, "NULL_RESPONSE", 200

        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        
        # Check for text response
        text_out = ""
        for p in parts:
            if "text" in p:
                text_out += p["text"]
        
        if text_out:
            return True, text_out.strip(), 200

        return True, json.dumps(candidates[0], ensure_ascii=False), 200

    except Exception as e:
        return False, str(e), None


async def ai_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.from_user:
        return

    user_id = msg.from_user.id
    chat_id = update.effective_chat.id
    prompt = ""

    if msg.text and msg.text.startswith("/ask"):
        prompt = " ".join(context.args) if context.args else ""
        await clear_ai_history(user_id, "gemini")
        _AI_ACTIVE_USERS.pop(user_id, None)

        if not prompt:
            return await msg.reply_text("<b>USAGE:</b> <code>/ask &lt;query&gt;</code>", parse_mode="HTML")

    elif msg.reply_to_message:
        if user_id not in _AI_ACTIVE_USERS:
            return await msg.reply_text("<b>ERROR:</b> Session required. Use /ask.")
        prompt = (msg.text or "").strip()

    if not prompt:
        return

    stop = asyncio.Event()
    typing = asyncio.create_task(_typing_loop(context.bot, chat_id, stop))

    try:
        final_prompt = await build_ai_prompt(user_id, prompt)
        ok, raw, status = await ask_ai_gemini(final_prompt)

        if not ok:
            if _is_gemini_quota_error(status, raw):
                history = await get_ai_history(user_id, "gemini")
                groq_history = _ai_history_to_groq(history)
                raw = await ask_groq_text(prompt=prompt, history=groq_history, use_search=False)
            else:
                raise RuntimeError(raw)

        clean = sanitize_ai_output(raw)
        chunks = split_message(clean, 4000)

        stop.set()
        typing.cancel()

        # Reply to the original message/reply to maintain thread
        reply_to_id = msg.message_id
        
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=chunks[0],
            reply_to_message_id=reply_to_id,
            parse_mode="HTML"
        )
        _AI_ACTIVE_USERS[user_id] = sent.message_id

        for part in chunks[1:]:
            await context.bot.send_message(
                chat_id=chat_id,
                text=part,
                parse_mode="HTML"
            )

        history = await get_ai_history(user_id, "gemini")
        history.append({"user": prompt, "ai": clean})
        await save_ai_history(user_id, history, "gemini")

    except Exception as e:
        stop.set()
        typing.cancel()
        await clear_ai_history(user_id, "gemini")
        _AI_ACTIVE_USERS.pop(user_id, None)
        await msg.reply_text(f"<b>ERROR:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")

