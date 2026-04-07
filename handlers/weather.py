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
        return await msg.reply_text("USAGE: /weather <location>", parse_mode="HTML")

    city = " ".join(context.args).strip()
    status_msg = await msg.reply_text(f"QUERY: Fetching meteorological data for {city.upper()}...", parse_mode="HTML")

    session = await get_http_session()
    url = f"https://wttr.in/{city}?format=j1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return await status_msg.edit_text("ERROR: Remote server unreachable.")
            data = await resp.json()
    except Exception:
        return await status_msg.edit_text("ERROR: Connection timeout.")

    try:
        current = data.get("current_condition", [{}])[0]
        weather_desc = current.get("weatherDesc", [{"value": "N/A"}])[0]["value"]
        temp_c = current.get("temp_C", "N/A")
        feels = current.get("FeelsLikeC", "N/A")
        humidity = current.get("humidity", "N/A")
        wind = f"{current.get('windspeedKmph','N/A')} km/h"
        cloud = current.get("cloudcover", "N/A")
    except Exception:
        return await status_msg.edit_text("ERROR: Data parsing failure.")

    report = (
        f"<b>METEOROLOGICAL REPORT: {city.upper()}</b>\n\n"
        f"CONDITION : {weather_desc}\n"
        f"TEMPERATURE : {temp_c} C (FEELS: {feels} C)\n"
        f"HUMIDITY : {humidity}%\n"
        f"WIND SPEED : {wind}\n"
        f"CLOUD COVER : {cloud}%\n\n"
        f"TIMESTAMP : {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await status_msg.edit_text(report, parse_mode="HTML")
