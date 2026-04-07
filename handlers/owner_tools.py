import os
import sys
import subprocess
import asyncio
import json
import logging
import html
import time
import io
import traceback
from contextlib import redirect_stdout
from typing import Dict, Any, List

from telegram import Update
from telegram.ext import ContextTypes

from utils.config import OWNER_ID, LOG_CHAT_ID

logger = logging.getLogger(__name__)

# BLACKLIST DATA (JSON Based)
BLACKLIST_PATH = "data/blacklist.json"

def _load_blacklist() -> List[int]:
    if not os.path.exists(BLACKLIST_PATH): return []
    try:
        with open(BLACKLIST_PATH, "r") as f:
            return json.load(f)
    except: return []

def _save_blacklist(ids: List[int]):
    os.makedirs("data", exist_ok=True)
    with open(BLACKLIST_PATH, "w") as f:
        json.dump(ids, f)

def is_blacklisted(user_id: int) -> bool:
    return user_id in _load_blacklist()

# --- IMPROVED EVAL TOOLS ---

async def eval_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes arbitrary Python code with async support."""
    if update.effective_user.id not in OWNER_ID:
        return

    # Join the arguments to get the full code
    code = " ".join(context.args)
    if not code:
        return await update.message.reply_text("Contoh: <code>$eval print(1+1)</code>", parse_mode="HTML")

    # Clean the code from backticks if user wraps it in a code block
    if code.startswith("```") and code.endswith("```"):
        code = "\n".join(code.split("\n")[1:-1])

    import json, math, re, datetime, subprocess, random, urllib, requests, aiohttp, inspect, telegram
    
    # Provide useful local variables and heavily declared modules
    env = {
        "update": update,
        "context": context,
        "bot": context.bot,
        "chat": update.effective_chat,
        "user": update.effective_user,
        "asyncio": asyncio,
        "os": os,
        "sys": sys,
        "time": time,
        "json": json,
        "math": math,
        "re": re,
        "datetime": datetime,
        "subprocess": subprocess,
        "random": random,
        "urllib": urllib,
        "requests": requests,
        "aiohttp": aiohttp,
        "inspect": inspect,
        "telegram": telegram,
        "OWNER_ID": OWNER_ID,
    }

    # Output capture
    stdout = io.StringIO()
    
    # Pre-formatting for multiline support
    to_compile = f"async def func():\n" + "\n".join(f"    {line}" for line in code.split("\n"))

    try:
        # Define the function
        exec(to_compile, env)
        func = env["func"]
        
        # Execute and redirect stdout
        with redirect_stdout(stdout):
            start_time = time.time()
            await func()
            duration = time.time() - start_time
            
        output = stdout.getvalue()
        
        # Format the response in In/Out style
        result_text = (
            f"<b>In:</b>\n"
            f"<pre><code class=\"language-python\">{html.escape(code)}</code></pre>\n\n"
            f"<b>Out:</b> (<code>{duration:.4f}s</code>)\n"
        )
        
        if output:
            if len(output) > 3500:
                output = output[:3500] + "\n[Output truncated...]"
            result_text += f"<pre><code>{html.escape(output)}</code></pre>"
        else:
            result_text += "<i>No output returned.</i>"

        await update.message.reply_text(result_text, parse_mode="HTML")

    except Exception:
        # Capture error and traceback
        error_msg = traceback.format_exc()
        error_text = (
            f"<b>In:</b>\n"
            f"<pre><code class=\"language-python\">{html.escape(code)}</code></pre>\n\n"
            f"<b>Error:</b>\n"
            f"<pre><code>{html.escape(error_msg[-3500:])}</code></pre>"
        )
        await update.message.reply_text(error_text, parse_mode="HTML")

# --- SHELL TOOLS ---

async def sh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes shell commands."""
    if update.effective_user.id not in OWNER_ID:
        return

    cmd = " ".join(context.args)
    if not cmd:
        return await update.message.reply_text("Contoh: <code>$sh ls -la</code>", parse_mode="HTML")

    msg = await update.message.reply_text("<code>Running...</code>", parse_mode="HTML")
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output = (stdout.decode() or stderr.decode() or "Process finished with no output.").strip()
        
        if len(output) > 3800:
            output = output[:3800] + "\n[Output truncated]"
            
        await msg.edit_text(f"<b>Output:</b>\n<code>{html.escape(output)}</code>", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"<b>System Error:</b>\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

# --- BLACKLIST TOOLS ---

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_ID: return
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: target_id = int(context.args[0])
        except: pass
    if not target_id: return await update.message.reply_text("Tentukan ID pengguna.")
    
    blacklist = _load_blacklist()
    if target_id not in blacklist:
        blacklist.append(target_id)
        _save_blacklist(blacklist)
        await update.message.reply_text(f"ID <code>{target_id}</code> telah diblokir secara global.", parse_mode="HTML")
    else:
        await update.message.reply_text("ID sudah ada di daftar blokir.")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_ID: return
    try:
        target_id = int(context.args[0])
        blacklist = _load_blacklist()
        if target_id in blacklist:
            blacklist.remove(target_id)
            _save_blacklist(blacklist)
            await update.message.reply_text(f"ID <code>{target_id}</code> telah dipulihkan.", parse_mode="HTML")
        else:
            await update.message.reply_text("ID tidak ditemukan di daftar blokir.")
    except:
        await update.message.reply_text("Masukkan ID pengguna.")
