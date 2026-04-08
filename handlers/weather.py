import time
import asyncio
import aiohttp
import html

from telegram import Update
from telegram.ext import ContextTypes
from utils.http import get_http_session


async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if not context.args:
        return await msg.reply_text("<b>USAGE:</b> <code>.weather [location]</code>\nExample: <code>.weather Jakarta</code>", parse_mode="HTML")


    city = " ".join(context.args).strip()
    status_msg = await msg.reply_text(f"<b>SCANNING...</b>\nEstablishing meteorological uplink for <code>{html.escape(city.title())}</code>...", parse_mode="HTML")

    session = await get_http_session()
    # format=j1 gives full JSON, but we can also use format=3 for a simpler string if needed.
    # We stick with j1 for detailed technical vibe.
    url = f"https://wttr.in/{city}?format=j1"
    headers = {"User-Agent": "Mozilla/5.0 (Bot)"}

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                await status_msg.edit_text("<b>UPLINK FAILURE</b>\nMeteorological server returned non-standard status.", parse_mode="HTML")
                await asyncio.sleep(5)
                return await status_msg.delete()
            data = await resp.json()
    except Exception as e:
        await status_msg.edit_text(f"<b>TIMEOUT / ERROR</b>\nConnection dropped: <code>{html.escape(str(e))}</code>", parse_mode="HTML")
        await asyncio.sleep(5)
        return await status_msg.delete()

    try:
        current = data.get("current_condition", [{}])[0]
        weather_desc = current.get("weatherDesc", [{"value": "Unknown"}])[0]["value"]
        temp_c = current.get("temp_C", "N/A")
        feels = current.get("FeelsLikeC", "N/A")
        humidity = current.get("humidity", "N/A")
        wind = f"{current.get('windspeedKmph','N/A')} km/h"
        vis = f"{current.get('visibility', 'N/A')} km"
        
        # Get location info
        nearest = data.get("nearest_area", [{}])[0]
        area = nearest.get("areaName", [{"value": city.title()}])[0]["value"]
        country = nearest.get("country", [{"value": ""}])[0]["value"]
        loc_str = f"{area}, {country}" if country else area

    except Exception:
        return await status_msg.edit_text("<b>STRUCTURAL FAULT</b>\nFailed to parse meteorological data stream.", parse_mode="HTML")

    report = (
        f"<b>METEOROLOGICAL REPORT</b>\n"
        f"• NODE      : <code>{html.escape(loc_str)}</code>\n"
        f"• CONDITION : <code>{weather_desc}</code>\n"
        f"• THERMAL   : <code>{temp_c}°C</code> (RealFeel: {feels}°C)\n"
        f"• HUMIDITY  : <code>{humidity}%</code>\n"
        f"• WIND      : <code>{wind}</code>\n"
        f"• VISIBILITY: <code>{vis}</code>\n\n"
        f"<i>Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
    )
    
    await status_msg.edit_text(report, parse_mode="HTML")
