import random
import time
import logging

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
)
from telegram.ext import ContextTypes

from utils.config import OWNER_ID
from database.welcome_db import (
    init_welcome_db,
    load_welcome_chats,
    save_welcome_chats,
    load_verified,
    save_verified_user,
    save_pending_welcome,
    pop_pending_welcome,
)

log = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

WELCOME_ENABLED_CHATS = set()
VERIFIED_USERS = {}
PENDING_VERIFY = {}
WELCOME_MESSAGES = {}


def generate_math_question(user_id: int, chat_id: int):
    op = random.choice(["+", "-"])

    if op == "+":
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        answer = a + b
    else:
        a = random.randint(20, 99)
        b = random.randint(1, 50)
        if b > a:
            a, b = b, a
        answer = a - b

    wrong = set()
    while len(wrong) < 3:
        x = random.randint(answer - 30, answer + 30)
        if x != answer and x >= 0:
            wrong.add(x)

    options = list(wrong) + [answer]
    random.shuffle(options)

    PENDING_VERIFY[user_id] = {
        "chat_id": chat_id,
        "answer": answer
    }

    buttons = [
        [InlineKeyboardButton(str(o), callback_data=f"verify_ans:{chat_id}:{user_id}:{o}")]
        for o in options
    ]

    text = (
        "Answer the following math question\n\n"
        f"<b>{a} {op} {b} = ?</b>\n\n"
    )

    return text, InlineKeyboardMarkup(buttons)


def verify_keyboard(user_id: int, chat_id: int, bot_username: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Verify",
                url=f"https://t.me/{bot_username}?start=verify_{chat_id}_{user_id}"
            )
        ]
    ])


async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat

    if user.id in OWNER_ID:
        return True

    if chat.type not in ("group", "supergroup"):
        return False

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


def wlc_keyboard(chat_id: int):
    status = "ACTIVE" if chat_id in WELCOME_ENABLED_CHATS else "DISABLE"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Status: {status}", callback_data="wlc_toggle:ignore"),
        ],
        [
            InlineKeyboardButton("ENABLE", callback_data=f"wlc_toggle:{chat_id}:enable"),
            InlineKeyboardButton("DISABLE", callback_data=f"wlc_toggle:{chat_id}:disable"),
        ],
        [
            InlineKeyboardButton("Tutup Menu", callback_data=f"wlc_toggle:{chat_id}:close")
        ]
    ])

async def wlc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WELCOME_ENABLED_CHATS
    msg = update.message
    chat = update.effective_chat
    if not msg or not chat: return
    
    if chat.type == "private":
        return await msg.reply_text("<b>ERROR:</b> Perintah ini wajib digunakan di dalam Grup.", parse_mode="HTML")

    if not await is_admin_or_owner(update, context):
        return await msg.reply_text("<b>ERROR:</b> Hanya Admin / Owner yang dapat menyetel ini.", parse_mode="HTML")

    await msg.reply_text(
        "<b>Security & Welcome Controls </b>\n"
        "Gunakan menu interaktif di bawah ini untuk menghidupkan Captcha/Welcome Message:",
        reply_markup=wlc_keyboard(chat.id),
        parse_mode="HTML"
    )

async def wlc_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WELCOME_ENABLED_CHATS
    q = update.callback_query
    
    parts = q.data.split(':')
    if len(parts) != 3 or parts[1] == "ignore":
        return await q.answer()
        
    chat_id = int(parts[1])
    action = parts[2]
    
    if action == "close":
        await q.answer()
        return await q.message.delete()
        
    if action == "enable":
        WELCOME_ENABLED_CHATS.add(chat_id)
        save_welcome_chats(WELCOME_ENABLED_CHATS)
        await q.answer("Pengaturan Disimpan: AKTIF")
    elif action == "disable":
        WELCOME_ENABLED_CHATS.discard(chat_id)
        save_welcome_chats(WELCOME_ENABLED_CHATS)
        await q.answer("Pengaturan Disimpan: MATI")
        
    try:
        await q.edit_message_reply_markup(reply_markup=wlc_keyboard(chat_id))
    except Exception:
        pass


async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat

    if chat.id not in WELCOME_ENABLED_CHATS:
        return

    for user in msg.new_chat_members:
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
        except Exception as e:
            log.warning(f"Failed to restrict user {user.id} in chat {chat.id}: {e}")

        username = f"@{user.username}" if user.username else "—"
        fullname = user.full_name
        chatname = chat.title or "this group"

        caption = (
            f"<b>Access Granted </b>\n"
            f"User Identity : <code>{fullname}</code>\n"
            f"Registry ID   : <code>{user.id}</code>\n"
            f"Sys Username  : {username}\n\n"
            f"<i>Execution requires verification clearance.</i>"
        )

        try:
            photos = await context.bot.get_user_profile_photos(user_id=user.id, limit=1)
            if photos.total_count > 0:
                sent = await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=photos.photos[0][-1].file_id,
                    caption=caption,
                    reply_markup=verify_keyboard(user.id, chat.id, context.bot.username),
                    parse_mode="HTML"
                )
            else:
                sent = await msg.reply_text(
                    caption,
                    reply_markup=verify_keyboard(user.id, chat.id, context.bot.username),
                    parse_mode="HTML"
                )
        except Exception:
            sent = await msg.reply_text(
                caption,
                reply_markup=verify_keyboard(user.id, chat.id, context.bot.username),
                parse_mode="HTML"
            )

        WELCOME_MESSAGES[user.id] = (chat.id, sent.message_id)
        try:
            save_pending_welcome(chat.id, user.id, sent.message_id)
        except Exception:
            pass


async def start_verify_pm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return

    arg = context.args[0]
    if not arg.startswith("verify_"):
        return

    _, chat_id, user_id = arg.split("_")
    chat_id = int(chat_id)
    user_id = int(user_id)

    if update.effective_user.id != user_id:
        return

    text, keyboard = generate_math_question(user_id, chat_id)

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def verify_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VERIFIED_USERS

    q = update.callback_query

    _, chat_id, user_id, chosen = q.data.split(":")
    chat_id = int(chat_id)
    user_id = int(user_id)
    chosen = int(chosen)

    if q.from_user.id != user_id:
        await q.answer("Not your button.", show_alert=True)
        return

    pending = PENDING_VERIFY.get(user_id)
    if not pending or pending["chat_id"] != chat_id:
        await q.answer("Invalid verification.", show_alert=True)
        return

    if chosen != pending["answer"]:
        await q.answer("Wrong answer. Try again.", show_alert=True)
        text, keyboard = generate_math_question(user_id, chat_id)
        try:
            await q.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            await q.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    await q.answer("Verification successful!", show_alert=False)

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_invite_users=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_messages=True,
                can_send_other_messages=True,
                can_send_photos=True,
                can_send_polls=True,
                can_send_video_notes=True,
                can_send_videos=True,
                can_send_voice_notes=True,
            )
        )
    except Exception:
        pass

    VERIFIED_USERS.setdefault(chat_id, set()).add(user_id)
    try:
        save_verified_user(chat_id, user_id)
    except Exception:
        pass

    PENDING_VERIFY.pop(user_id, None)

    msg_id = None
    if user_id in WELCOME_MESSAGES:
        try:
            g_chat_id, m_id = WELCOME_MESSAGES.pop(user_id)
            if g_chat_id == chat_id:
                msg_id = m_id
        except Exception:
            msg_id = None

    if msg_id is None:
        try:
            msg_id = pop_pending_welcome(chat_id, user_id)
        except Exception:
            msg_id = None

    if msg_id:
        try:
            await context.bot.delete_message(chat_id, msg_id)
        except Exception:
            pass

    try:
        await q.message.edit_text("Verification successful. You may return to the group.")
    except Exception:
        try:
            await context.bot.send_message(
                chat_id=q.message.chat_id,
                text="Verification successful. You may return to the group."
            )
        except Exception:
            pass


try:
    init_welcome_db()
except Exception:
    pass

try:
    WELCOME_ENABLED_CHATS = load_welcome_chats()
except Exception:
    WELCOME_ENABLED_CHATS = set()

try:
    VERIFIED_USERS = load_verified()
except Exception:
    VERIFIED_USERS = {}
    