import html
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from database.moderation_db import moderation_is_enabled
from .auth import is_admin_or_owner
from .helpers import (
    mention_html,
    display_name,
    display_name_from_token,
    extract_duration_target_reason,
    extract_target_reason,
    resolve_target_user_id,
    resolve_target_user_obj_for_display,
    resolve_user_obj_for_display_by_id,
)
from .permissions import MUTED_PERMISSIONS, UNMUTED_PERMISSIONS


async def _resolve_target_display(update: Update, context: ContextTypes.DEFAULT_TYPE, target_token: str | None):
    target_id = await resolve_target_user_id(update, context, target_token)
    if not target_id:
        return None, None

    obj = await resolve_target_user_obj_for_display(update, context, target_token)
    if not obj:
        obj = await resolve_user_obj_for_display_by_id(update, context, int(target_id))

    name = display_name(obj) or display_name_from_token(target_token)
    who = mention_html(int(target_id), name)
    return int(target_id), who


async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat

    if not msg or not chat:
        return

    if chat.type not in ("group", "supergroup"):
        return

    if not moderation_is_enabled(chat.id):
        return

    if not await is_admin_or_owner(update, context):
        return await msg.reply_text("ERROR: UNAUTHORIZED")

    has_reply = bool(msg.reply_to_message and msg.reply_to_message.from_user)
    until, dur_human, target_token, reason = extract_duration_target_reason(context.args or [], has_reply)

    target_id, who = await _resolve_target_display(update, context, target_token)
    if not target_id:
        return await msg.reply_text(
            "<b>USAGE:</b>\n"
            "• <code>.ban 7d [id|@user] [reason]</code>\n"
            "• Reply with <code>.ban 7d [reason]</code>",
            parse_mode="HTML",
        )

    try:
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=int(target_id), until_date=until)
        duration_text = f"<b>DURATION:</b> {html.escape(dur_human)}\n" if dur_human else "<b>DURATION:</b> PERMANENT\n"
        return await msg.reply_text(
            "<b>BANNED</b>\n"
            f"<b>USER:</b> {who}\n"
            f"{duration_text}"
            f"<b>REASON:</b> <code>{html.escape(reason)}</code>",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        return await msg.reply_text(
            f"<b>ERROR:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
        )

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat
    if not msg or not chat: return
    if chat.type not in ("group", "supergroup"): return
    if not moderation_is_enabled(chat.id): return

    if not await is_admin_or_owner(update, context):
        return await msg.reply_text("ERROR: UNAUTHORIZED")

    has_reply = bool(msg.reply_to_message and msg.reply_to_message.from_user)
    _, _, target_token, _ = extract_duration_target_reason(context.args or [], has_reply)

    target_id, who = await _resolve_target_display(update, context, target_token)
    if not target_id:
        return await msg.reply_text("<b>USAGE:</b> <code>.unban [id|@user]</code>", parse_mode="HTML")

    try:
        await context.bot.unban_chat_member(chat_id=chat.id, user_id=int(target_id))
        return await msg.reply_text(
            "<b>RESTORED</b>\n"
            f"<b>USER:</b> {who}",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        return await msg.reply_text(
            f"<b>ERROR:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
        )

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat
    if not msg or not chat: return
    if chat.type not in ("group", "supergroup"): return
    if not moderation_is_enabled(chat.id): return

    if not await is_admin_or_owner(update, context):
        return await msg.reply_text("ERROR: UNAUTHORIZED")

    has_reply = bool(msg.reply_to_message and msg.reply_to_message.from_user)
    until, dur_human, target_token, reason = extract_duration_target_reason(context.args or [], has_reply)

    target_id, who = await _resolve_target_display(update, context, target_token)
    if not target_id:
        return await msg.reply_text(
            "<b>USAGE:</b>\n"
            "• <code>.mute 10m [id|@user] [reason]</code>\n"
            "• Reply with <code>.mute 10m [reason]</code>",
            parse_mode="HTML",
        )

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=int(target_id),
            permissions=MUTED_PERMISSIONS,
            until_date=until,
        )
        duration_text = f"<b>DURATION:</b> {html.escape(dur_human)}\n" if dur_human else "<b>DURATION:</b> PERMANENT\n"
        return await msg.reply_text(
            "<b>MUTED</b>\n"
            f"<b>USER:</b> {who}\n"
            f"{duration_text}"
            f"<b>REASON:</b> <code>{html.escape(reason)}</code>",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        return await msg.reply_text(f"<b>ERROR:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat
    if not msg or not chat: return
    if chat.type not in ("group", "supergroup"): return
    if not moderation_is_enabled(chat.id): return

    if not await is_admin_or_owner(update, context):
        return await msg.reply_text("ERROR: UNAUTHORIZED")

    has_reply = bool(msg.reply_to_message and msg.reply_to_message.from_user)
    _, _, target_token, _ = extract_duration_target_reason(context.args or [], has_reply)

    target_id, who = await _resolve_target_display(update, context, target_token)
    if not target_id:
        return await msg.reply_text("<b>USAGE:</b> <code>.unmute [id|@user]</code>", parse_mode="HTML")

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=int(target_id),
            permissions=UNMUTED_PERMISSIONS,
            until_date=None,
        )
        return await msg.reply_text(
            "<b>ACTIVE</b>\n"
            f"<b>USER:</b> {who}",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        return await msg.reply_text(f"<b>ERROR:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def kick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat
    if not msg or not chat: return
    if chat.type not in ("group", "supergroup"): return
    if not moderation_is_enabled(chat.id): return

    if not await is_admin_or_owner(update, context):
        return await msg.reply_text("ERROR: UNAUTHORIZED")

    has_reply = bool(msg.reply_to_message and msg.reply_to_message.from_user)
    target_token, reason = extract_target_reason(context.args or [], has_reply)

    target_id, who = await _resolve_target_display(update, context, target_token)
    if not target_id:
        return await msg.reply_text(
            "<b>USAGE:</b>\n"
            "• <code>.kick [id|@user] [reason]</code>\n"
            "• Reply with <code>.kick [reason]</code>",
            parse_mode="HTML",
        )

    try:
        until = datetime.now(timezone.utc) + timedelta(seconds=45)
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=int(target_id), until_date=until)
        await context.bot.unban_chat_member(chat_id=chat.id, user_id=int(target_id), only_if_banned=True)
        return await msg.reply_text(
            "<b>EJECTED</b>\n"
            f"<b>USER:</b> {who}\n"
            f"<b>REASON:</b> <code>{html.escape(reason)}</code>",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        return await msg.reply_text(f"<b>ERROR:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")