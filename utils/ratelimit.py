import time
import asyncio
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

# Simple in-memory rate limiter: {user_id: [last_request_timestamps]}
_USER_HISTORY = {}

def rate_limit(limit: int = 5, window: int = 10):
    """
    Rate limiting decorator for command handlers.
    limit: max commands in the window
    window: time window in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user:
                return await func(update, context, *args, **kwargs)

            user_id = update.effective_user.id
            now = time.time()

            if user_id not in _USER_HISTORY:
                _USER_HISTORY[user_id] = []

            # Cleanup old timestamps
            _USER_HISTORY[user_id] = [t for t in _USER_HISTORY[user_id] if now - t < window]

            if len(_USER_HISTORY[user_id]) >= limit:
                # Silent drop or warning? Professional tools often stay silent.
                # We can send a prompt alert once.
                try:
                    # We only alert if it's exactly at the limit to avoid spamming the warning
                    if len(_USER_HISTORY[user_id]) == limit:
                        await update.effective_message.reply_text(
                            "<b>ERROR: RATELIMIT_EXCEEDED</b>\nCooldown active.",
                            parse_mode="HTML"
                        )
                except Exception:
                    pass
                return

            _USER_HISTORY[user_id].append(now)
            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator
