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
    status_msg = await msg.reply_text(f"Fetching data for: <code>{html.escape(city.title())}</code>...", parse_mode="HTML")

    session = await get_http_session()
    # format=j1 gives full JSON, but we can also use format=3 for a simpler string if needed.
    # We stick with j1 for detailed technical vibe.
    url = f"https://wttr.in/{city}?format=j1"
    headers = {"User-Agent": "Mozilla/5.0 (Bot)"}

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                await status_msg.edit_text("<b>ERROR</b>\nMETEOR SERVER UNREACHABLE", parse_mode="HTML")
                await asyncio.sleep(5)
                return await status_msg.delete()
            data = await resp.json()
    except Exception as e:
        await status_msg.edit_text(f"<b>ERROR</b>\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
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
        loc_str = loc_str.upper()

    except Exception:
        return await status_msg.edit_text("<b>ERROR</b>\nDATA PARSING FAILED", parse_mode="HTML")

    report = (
        f"<b>WEATHER REPORT</b>\n"

        f"• LOCATION: <code>{html.escape(loc_str)}</code>\n"
        f"• SUMMARY : <code>{weather_desc.upper()}</code>\n"
        f"• TEMP    : <code>{temp_c}°C</code> (Feels like {feels}°C)\n"
        f"• HUMIDITY: <code>{humidity}%</code>\n"
        f"• WIND    : <code>{wind}</code>\n"
        f"• VISIB   : <code>{vis}</code>\n\n"
        f"<i>{time.strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
    )

    
    await status_msg.edit_text(report, parse_mode="HTML")
