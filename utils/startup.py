import asyncio
import logging

from handlers.welcome import load_welcome_chats, init_welcome_db, load_verified
from database import premium_service

log = logging.getLogger(__name__)


async def startup_tasks(app):
    log.info("✓ Running startup tasks...")

    try:
        init_welcome_db()
        load_welcome_chats()
        load_verified()
        log.info("✓ Welcome cache loaded")
    except Exception as e:
        log.warning(f"Startup cache load failed: {e}")

    try:
        premium_service.init()
        log.info("✓ Premium cache initialized")
    except Exception as e:
        log.warning(f"Premium init failed: {e}")

    await asyncio.sleep(2)
