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

import ast

async def eval_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes arbitrary Python code natively with AST return transformation."""
    if update.effective_user.id not in OWNER_ID:
        return

    code = " ".join(context.args)
    if not code:
        return await update.message.reply_text("Contoh: <code>$eval 1 + 1</code>", parse_mode="HTML")

    if code.startswith("```") and code.endswith("```"):
        code = "\n".join(code.split("\n")[1:-1])
    code = code.strip()

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
        "OWNER_ID": OWNER_ID,
    }

    stdout = io.StringIO()
    try:
        parsed_body = ast.parse(code)
        
        # Modify last statement to return its value if it's an expression
        if parsed_body.body and isinstance(parsed_body.body[-1], ast.Expr):
            ret_node = ast.Return(value=parsed_body.body[-1].value)
            ast.copy_location(ret_node, parsed_body.body[-1])
            parsed_body.body[-1] = ret_node
            
        # Wrap everything inside an async function
        wrapper = ast.parse("async def __aexec(): pass")
        wrapper.body[0].body = parsed_body.body
        ast.fix_missing_locations(wrapper)

        exec(compile(wrapper, filename="<ast>", mode="exec"), env)
        func = env["__aexec"]
        
        start_time = time.perf_counter()
        with redirect_stdout(stdout):
            returned_value = await func()
        duration = time.perf_counter() - start_time
        
        output = stdout.getvalue()
        
        # Formatting result natively
        result_text = f"<b>[ EVALUASI SUKSES ]</b>  —  <code>{duration:.4f}s</code>\n"
        
        if output:
            result_text += f"\n<b>Stdout:</b>\n<pre><code>{html.escape(output[:3500])}</code></pre>"
            
        if returned_value is not None:
            # Prevent token overflow if object is massive
            val_str = str(returned_value)
            type_str = type(returned_value).__name__
            result_text += f"\n<b>Return</b> (<code>{type_str}</code>)<b>:</b>\n<pre><code>{html.escape(val_str[:3500])}</code></pre>"
            
        if not output and returned_value is None:
            result_text += "\n<i>(Executed without return/stdout)</i>"
            
        await update.message.reply_text(result_text, parse_mode="HTML")

    except Exception:
        error_msg = traceback.format_exc()
        error_text = (
            f"<b>[ TRACEBACK EXCEPTION ]</b>\n"
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
