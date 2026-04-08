import os
import time
import uuid
import mimetypes
import aiohttp
import aiofiles
from urllib.parse import urlparse, unquote

from utils.http import get_http_session
from .constants import TMP_DIR
from .utils import sanitize_filename, progress_bar
from .instagram_scrape import (
    igdl_download_for_fallback,
    send_instagram_fallback_result,
    cleanup_instagram_fallback_result,
)

INSTAGRAM_API_URL = "https://api.sonzaix.indevs.in/sosmed/instagram"


def is_instagram_url(url: str) -> bool:
    try:
        host = (urlparse((url or "").strip()).hostname or "").lower()
        return host == "instagram.com" or host.endswith(".instagram.com") or host == "instagr.am"
    except Exception:
        text = (url or "").lower()
        return "instagram.com" in text or "instagr.am" in text


def _guess_ext_from_url(url: str) -> str:
    try:
        path = unquote(urlparse(url).path or "")
        ext = os.path.splitext(path)[1].lower()
        if ext in (".mp4", ".mov", ".m4v", ".jpg", ".jpeg", ".png", ".webp"):
            return ext
    except Exception:
        pass
    return ""


def _guess_ext(content_type: str, media_type: str, media_url: str) -> str:
    ext = _guess_ext_from_url(media_url)
    if ext:
        return ext

    ctype = (content_type or "").split(";")[0].strip().lower()
    guessed = mimetypes.guess_extension(ctype) or ""
    if guessed:
        return guessed

    if media_type == "video":
        return ".mp4"
    return ".jpg"


def _build_title(data: dict, media_type: str) -> str:
    nickname = (data.get("nickname") or "").strip()
    username = (data.get("username") or "").strip()
    description = (data.get("description") or "").strip()

    if nickname and username:
        base = f"{nickname} (@{username})"
    elif nickname:
        base = nickname
    elif username:
        base = f"@{username}"
    else:
        base = "Instagram Media"

    if description:
        short_desc = description[:80].strip()
        return f"{base} - {short_desc}"

    if media_type == "video":
        return f"{base} - Instagram Video"

    return f"{base} - Instagram Image"


def _extract_media_candidates(data: dict) -> list[tuple[str, str]]:
    out = []

    def add_candidate(kind: str, url: str):
        u = (url or "").strip()
        if not u:
            return
        item = (kind, u)
        if item not in out:
            out.append(item)

    add_candidate("video", data.get("video_url"))
    add_candidate("photo", data.get("image_url"))
    add_candidate("photo", data.get("photo_url"))
    add_candidate("photo", data.get("image"))
    add_candidate("photo", data.get("thumbnail"))

    for key in ("images", "image_urls", "photos"):
        items = data.get(key) or []
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    add_candidate("photo", item)
                elif isinstance(item, dict):
                    add_candidate("photo", item.get("url") or item.get("image") or item.get("src"))

    for key in ("videos", "video_urls"):
        items = data.get(key) or []
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    add_candidate("video", item)
                elif isinstance(item, dict):
                    add_candidate("video", item.get("url") or item.get("video") or item.get("src"))

    for key in ("media", "medias", "items", "carousel", "carousel_media"):
        items = data.get(key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, str):
                add_candidate("photo", item)
                continue
            if not isinstance(item, dict):
                continue

            media_type = str(
                item.get("type")
                or item.get("media_type")
                or item.get("kind")
                or ""
            ).lower()

            media_url = (
                item.get("url")
                or item.get("download_url")
                or item.get("media_url")
                or item.get("video_url")
                or item.get("image_url")
                or item.get("src")
            )

            if not media_url:
                continue

            if "video" in media_type or media_type in ("2", "clip", "reel"):
                add_candidate("video", media_url)
            else:
                add_candidate("photo", media_url)

    return out


def _pick_media_for_format(candidates: list[tuple[str, str]], fmt_key: str) -> tuple[str, str] | None:
    if not candidates:
        return None

    if fmt_key == "mp3":
        for kind, url in candidates:
            if kind == "video":
                return kind, url
        return None

    for kind, url in candidates:
        if kind == "video":
            return kind, url

    return candidates[0]


async def cobalt_api_fetch(url: str) -> dict | None:
    session = await get_http_session()
    try:
        async with session.post(
            "https://cobalt.tools/api/json",
            json={"url": url, "videoQuality": "1080", "isAudioOnly": False},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": "https://cobalt.tools",
                "Referer": "https://cobalt.tools/",
            },
            timeout=aiohttp.ClientTimeout(total=20),
        ) as resp:
            data = await resp.json()
            if data.get("status") == "stream" or data.get("status") == "picker":
                return data
    except Exception as e:
        print("Cobalt API Error", e)
    return None

async def instagram_api_download(
    raw_url: str,
    fmt_key: str,
    bot,
    chat_id,
    status_msg_id,
):
    session = await get_http_session()

    async def update_status(text: str):
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception:
            pass

    await update_status("Querying metadata...")

    # Primary: Sonzai
    try:
        async with session.get(
            INSTAGRAM_API_URL,
            params={"url": raw_url},
            timeout=aiohttp.ClientTimeout(total=20),
        ) as resp:
            data = await resp.json(content_type=None)

        if isinstance(data, dict) and str(data.get("status") or "").lower() == "success":
            candidates = _extract_media_candidates(data)
            picked = _pick_media_for_format(candidates, fmt_key)
            if picked:
                media_type, media_url = picked
                title = _build_title(data, media_type)
                
                # Try download
                path = await _download_file(session, media_url, title, bot, chat_id, status_msg_id)
                if path:
                    return {"path": path, "title": title}
    except Exception as e:
        print("Instagram Sonzai Failed", repr(e))

    # Secondary: Cobalt
    await update_status("Synchronizing secondary node...")
    try:
        data = await cobalt_api_fetch(raw_url)
        if data:
            if data.get("status") == "stream":
                media_url = data.get("url")
                title = "Instagram Media"
                path = await _download_file(session, media_url, title, bot, chat_id, status_msg_id)
                if path:
                    return {"path": path, "title": title}
            elif data.get("status") == "picker":
                picker_items = data.get("picker") or []
                # If picker, we return multiple items
                downloaded = []
                for idx, item in enumerate(picker_items):
                    p_url = item.get("url")
                    if p_url:
                        p_path = await _download_file(session, p_url, f"Item {idx}", bot, chat_id, status_msg_id, silent=True)
                        if p_path:
                            downloaded.append({"path": p_path, "type": "video" if "video" in (item.get("type") or "") else "photo"})
                
                if downloaded:
                    return {"items": downloaded, "title": "Instagram Media"}
    except Exception as e:
        print("Cobalt Failed", e)

    # Tertiary: Scraper Fallback (Indown/SnapSave)
    await update_status("Executing legacy fallback protocol...")
    return await igdl_download_for_fallback(
        bot=bot,
        chat_id=chat_id,
        reply_to=None,
        status_msg_id=status_msg_id,
        url=raw_url,
    )

async def _download_file(session, url, title, bot, chat_id, status_msg_id, silent=False):
    # Standard header mimic
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }
    
    # Referer logic
    if "cdninstagram.com" in url or "fbcdn.net" in url:
        headers["Referer"] = "https://www.instagram.com/"
        headers["Origin"] = "https://www.instagram.com"

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as resp:
            if resp.status >= 400:
                print(f"Download Error {resp.status} for {url}")
                return None
                
            total = int(resp.headers.get("Content-Length", 0))
            content_type = resp.headers.get("Content-Type", "")
            
            # Simplified media type for ext guessing
            m_type = "video" if "video" in content_type else "photo"
            ext = _guess_ext(content_type, m_type, url)
            
            out_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}_{sanitize_filename(title)}{ext}")
            
            downloaded = 0
            last_edit = 0.0
            
            async with aiofiles.open(out_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(128 * 1024):
                    await f.write(chunk)
                    downloaded += len(chunk)
                    
                    if not silent and total and time.time() - last_edit >= 1.5:
                        pct = (downloaded / total) * 100
                        try:
                            await bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=status_msg_id,
                                text=f"Executing acquisition...\n<code>{progress_bar(pct)}</code>",
                                parse_mode="HTML"
                            )
                        except Exception: pass
                        last_edit = time.time()
            return out_path
    except Exception as e:
        print(f"File download failed: {e}")
        return None


async def send_instagram_result(bot, chat_id: int, reply_to: int, result: dict):
    if result.get("items"):
        await send_instagram_fallback_result(
            bot=bot,
            chat_id=chat_id,
            reply_to=reply_to,
            result=result,
        )
        return

    path = result.get("path")
    title = result.get("title") or "Instagram Media"

    if not path or not os.path.exists(path):
        raise RuntimeError("Instagram media file not found")

    with open(path, "rb") as f:
        if path.lower().endswith((".mp4", ".mov", ".m4v", ".webm")):
            await bot.send_video(
                chat_id=chat_id,
                video=f,
                caption=title,
                reply_to_message_id=reply_to,
                supports_streaming=True,
            )
        else:
            await bot.send_photo(
                chat_id=chat_id,
                photo=f,
                caption=title,
                reply_to_message_id=reply_to,
            )


async def cleanup_instagram_result(result: dict):
    await cleanup_instagram_fallback_result(result)