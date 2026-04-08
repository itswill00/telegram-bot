import time
import asyncio
import aiohttp

from telegram import Update
from telegram.ext import ContextTypes
from utils.http import get_http_session


async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if not context.args:
        return await msg.reply_text("<b>[ SYNTAX ERROR ]</b>\nCommand: <code>/weather [location]</code>", parse_mode="HTML")

    city = " ".join(context.args).strip()
    status_msg = await msg.reply_text(f"<b>[ FETCHING DATA ]</b>\nQuerying meteorological source for {city.title()}...", parse_mode="HTML")

    session = await get_http_session()
    url = f"https://wttr.in/{city}?format=j1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                await status_msg.edit_text("<b>[ CONNECTION FAILED ]</b>\nMeteorological server unreachable.", parse_mode="HTML")
                await asyncio.sleep(5)
                return await status_msg.delete()
            data = await resp.json()
    except Exception:
        await status_msg.edit_text("<b>[ TIMEOUT ]</b>\nConnection dropped.", parse_mode="HTML")
        await asyncio.sleep(5)
        return await status_msg.delete()

    try:
        current = data.get("current_condition", [{}])[0]
        weather_desc = current.get("weatherDesc", [{"value": "N/A"}])[0]["value"]
        temp_c = current.get("temp_C", "N/A")
        feels = current.get("FeelsLikeC", "N/A")
        humidity = current.get("humidity", "N/A")
        wind = f"{current.get('windspeedKmph','N/A')} km/h"
        cloud = current.get("cloudcover", "N/A")
    except Exception:
        return await status_msg.edit_text("<b>[ PARSE ERROR ]</b>\nMalformed structure.", parse_mode="HTML")

    report = (
        f"<b>[ METEOROLOGICAL SCAN ]</b>\n"
        f"<code>────────────────────────</code>\n"
        f"• Node Location : <code>{city.title()}</code>\n"
        f"• State         : <code>{weather_desc}</code>\n"
        f"• Thermal       : <code>{temp_c}°C</code> (Feels: {feels}°C)\n"
        f"• Humidity      : <code>{humidity}%</code>\n"
        f"• Wind Vector   : <code>{wind}</code>\n"
        f"• Cloud Cover   : <code>{cloud}%</code>\n\n"
        f"<i>Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}</i>"
    )
    
    await status_msg.edit_text(report, parse_mode="HTML")
