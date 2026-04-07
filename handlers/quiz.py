import json
import time
import asyncio
import html
import random
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.http import get_http_session
from utils.config import (
    GROQ_MODEL,
    GROQ_BASE,
    GROQ_KEY,
)

QUIZ_TIMEOUT = 30
QUIZ_TOTAL = 10

_ACTIVE_QUIZ: dict[int, dict] = {}

_QUESTION_STYLES = [
    "concept definition",
    "cause and effect",
    "logic check",
    "scenario analysis",
    "technical fact",
    "comparative logic",
]

def _quiz_keyboard(chat_id: int, qidx: int) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("A", callback_data=f"quizans:{chat_id}:{qidx}:A"),
            InlineKeyboardButton("B", callback_data=f"quizans:{chat_id}:{qidx}:B"),
        ],
        [
            InlineKeyboardButton("C", callback_data=f"quizans:{chat_id}:{qidx}:C"),
            InlineKeyboardButton("D", callback_data=f"quizans:{chat_id}:{qidx}:D"),
        ],
    ]
    return InlineKeyboardMarkup(rows)

def _render_question(q: dict, no: int) -> str:
    return (
        f"<b>TECHNICAL ASSESSMENT {no}/{QUIZ_TOTAL}</b>\n\n"
        f"<b>QUESTION:</b> {html.escape(q['question'])}\n\n"
        f"A. {html.escape(q['options']['A'])}\n"
        f"B. {html.escape(q['options']['B'])}\n"
        f"C. {html.escape(q['options']['C'])}\n"
        f"D. {html.escape(q['options']['D'])}\n\n"
        f"<i>Select A/B/C/D. Timeout: {QUIZ_TIMEOUT}s.</i>"
    )

def _strip_codeblock(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("```"):
        s = s.strip("`").strip()
        if s.lower().startswith("json"): s = s[4:].strip()
    return s

async def _generate_question_bank() -> list:
    seed = random.randint(100000, 999999)
    style = random.choice(_QUESTION_STYLES)
    prompt = (
        f"SEED:{seed}\nSTYLE: {style}\n"
        "Generate 10 technical/general knowledge MCQ in English.\n"
        "Format: JSON array of objects with 'question', 'options' (A,B,C,D), and 'answer' (A/B/C/D).\n"
        "No emojis. Pure JSON."
    )
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Professional assessment generator. No emojis."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
    }
    session = await get_http_session()
    async with session.post(f"{GROQ_BASE}/chat/completions", json=payload, headers={"Authorization": f"Bearer {GROQ_KEY}"}) as resp:
        if resp.status != 200: raise RuntimeError("API_FAILURE")
        data = await resp.json()
    raw = _strip_codeblock(data["choices"][0]["message"]["content"])
    bank = json.loads(raw)
    return bank[:QUIZ_TOTAL]

async def _send_or_edit_question(update: Update, context: ContextTypes.DEFAULT_TYPE, quiz: dict):
    chat_id = quiz["chat_id"]
    qidx = quiz["current"]
    q = quiz["bank"][qidx]
    text = _render_question(q, qidx + 1)
    kb = _quiz_keyboard(chat_id, qidx)
    quiz["start"] = time.time()
    quiz["answered"] = set()
    quiz["lock"] = False

    async def _timeout_guard():
        await asyncio.sleep(QUIZ_TIMEOUT + 0.2)
        live = _ACTIVE_QUIZ.get(chat_id)
        if not live or live is not quiz or quiz.get("current") != qidx or quiz.get("lock"): return
        quiz["lock"] = True
        if quiz["current"] >= QUIZ_TOTAL - 1:
            _ACTIVE_QUIZ.pop(chat_id, None)
            await context.bot.edit_message_text(chat_id=chat_id, message_id=quiz["message_id"], text="<b>ASSESSMENT COMPLETED</b>\nProcessing results...")
            await asyncio.sleep(2)
            return await _end_quiz(context, quiz)
        await context.bot.edit_message_text(chat_id=chat_id, message_id=quiz["message_id"], text="<b>TIMEOUT:</b> Moving to next query...")
        await asyncio.sleep(1)
        quiz["current"] += 1
        quiz["lock"] = False
        await _send_or_edit_question(update, context, quiz)

    quiz["timeout_task"] = context.application.create_task(_timeout_guard())
    if quiz.get("message_id"):
        try:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=quiz["message_id"], text=text, parse_mode="HTML", reply_markup=kb)
            return
        except Exception: pass
    sent = await (update.message.reply_text(text, parse_mode="HTML", reply_markup=kb) if update.message else context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb))
    quiz["message_id"] = sent.message_id

async def _end_quiz(context: ContextTypes.DEFAULT_TYPE, quiz: dict):
    chat_id = quiz["chat_id"]
    scores = quiz["scores"]
    if not scores: text = "<b>ASSESSMENT VOID:</b> No valid inputs detected."
    else:
        ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        lines = ["<b>ASSESSMENT ANALYTICS</b>\n"]
        for i, (uid, score) in enumerate(ranking, 1):
            lines.append(f"{i}. {uid} - SCORE: {score}")
        text = "\n".join(lines)
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg: return
    chat_id = update.effective_chat.id
    if chat_id in _ACTIVE_QUIZ: return await msg.reply_text("<b>WARN:</b> Assessment in progress.")
    try: bank = await _generate_question_bank()
    except Exception: return await msg.reply_text("<b>ERR:</b> Generator failure.")
    quiz = {"chat_id": chat_id, "current": 0, "scores": {}, "bank": bank, "message_id": None, "start": time.time(), "answered": set(), "lock": False}
    _ACTIVE_QUIZ[chat_id] = quiz
    await _send_or_edit_question(update, context, quiz)

async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q or not q.data: return
    try: _, cid_s, qidx_s, chosen = q.data.split(":", 3)
    except Exception: return await q.answer("DATA_ERR")
    quiz = _ACTIVE_QUIZ.get(int(cid_s))
    if not quiz or q.message.message_id != quiz.get("message_id") or int(qidx_s) != quiz["current"]: return await q.answer("STALE_SESSION")
    uid = q.from_user.id
    if uid in quiz["answered"]: return await q.answer("INPUT_LOCKED")
    quiz["answered"].add(uid)
    correct = quiz["bank"][quiz["current"]]["answer"]
    if chosen == correct:
        quiz["scores"][uid] = quiz["scores"].get(uid, 0) + 1
        await q.answer("SUCCESS: Correct.")
    else: await q.answer(f"FAILURE: Correct was {correct}.")
    if quiz.get("lock"): return
    quiz["lock"] = True
    if quiz["current"] >= QUIZ_TOTAL - 1:
        _ACTIVE_QUIZ.pop(int(cid_s), None)
        await context.bot.edit_message_text(chat_id=int(cid_s), message_id=quiz["message_id"], text="<b>ASSESSMENT COMPLETED</b>\nProcessing results...")
        await asyncio.sleep(2)
        return await _end_quiz(context, quiz)
    quiz["current"] += 1
    quiz["lock"] = False
    await _send_or_edit_question(update, context, quiz)
