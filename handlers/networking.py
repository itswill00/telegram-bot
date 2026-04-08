import html
import re
import socket
import aiohttp
import whois
import ipaddress

from telegram import Update
from telegram.ext import ContextTypes

from utils.http import get_http_session

#whois
def fmt_date(d):
    if isinstance(d, list):
        return str(d[0]) if d else "Not available"
    return str(d) if d else "Not available"


async def whoisdomain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "<b>WHOIS_QUERY</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>.whoisdomain google.com</code>",
            parse_mode="HTML"
        )

    domain = (
        context.args[0]
        .replace("http://", "")
        .replace("https://", "")
        .split("/")[0]
    )

    if not re.match(r"^[\w.-]+$", domain) or domain.startswith("-"):
        return await update.message.reply_text(
            "<b>ERROR</b>\nINVALID_DOMAIN_FORMAT",
            parse_mode="HTML"
        )

    msg = await update.message.reply_text(
        f"Processing: <code>{html.escape(domain)}</code>...",
        parse_mode="HTML"
    )

    try:
        w = whois.whois(domain)

        ns = w.name_servers
        if isinstance(ns, list):
            ns_text = "\n".join(f"• {html.escape(n)}" for n in ns[:8])
        else:
            ns_text = html.escape(str(ns)) if ns else "N/A"

        result = (
            "<b>WHOIS_INFORMATION</b>\n\n"
            f"<b>Domain:</b> <code>{html.escape(domain)}</code>\n"
            f"<b>Registrar:</b> {html.escape(str(w.registrar or 'N/A'))}\n"
            f"<b>WHOIS Server:</b> {html.escape(str(w.whois_server or 'N/A'))}\n\n"

            "<b>DATES</b>\n"
            f"<b>Created:</b> {fmt_date(w.creation_date)}\n"
            f"<b>Updated:</b> {fmt_date(w.updated_date)}\n"
            f"<b>Expires:</b> {fmt_date(w.expiration_date)}\n\n"

            "<b>REGISTRANT</b>\n"
            f"<b>Name:</b> {html.escape(str(w.name or 'N/A'))}\n"
            f"<b>Org:</b> {html.escape(str(w.org or 'N/A'))}\n"
            f"<b>Email:</b> {html.escape(str(w.emails[0] if isinstance(w.emails, list) else w.emails or 'N/A'))}\n\n"

            "<b>TECHNICAL</b>\n"
            f"<b>Status:</b> {html.escape(str(w.status or 'N/A'))}\n"
            f"<b>DNSSEC:</b> {html.escape(str(w.dnssec or 'N/A'))}\n\n"

            "<b>NAME_SERVERS</b>\n"
            f"{ns_text}\n\n"

            "<b>IANA_ID:</b> {html.escape(str(w.registrar_iana_id or 'N/A'))}\n"
            f"<b>URL:</b> {html.escape(str(w.registrar_url or 'N/A'))}"
        )

        if len(result) > 4096:
            await msg.edit_text(result[:4096], parse_mode="HTML")
            await update.message.reply_text(result[4096:], parse_mode="HTML")
        else:
            await msg.edit_text(result, parse_mode="HTML")

    except Exception as e:
        await msg.edit_text(
            f"<b>ERROR</b>\nWHOIS_FAILED: <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )
        
#cmd ip
async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "<b>IP_QUERY</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>.ip 8.8.8.8</code>",
            parse_mode="HTML"
        )

    ip = context.args[0]
    msg = await update.message.reply_text(
        f"Analyzing: <code>{html.escape(ip)}</code>...",
        parse_mode="HTML"
    )

    try:
        url = (
            f"http://ip-api.com/json/{ip}"
            "?fields=status,message,continent,continentCode,country,countryCode,"
            "region,regionName,city,zip,lat,lon,timezone,offset,isp,org,as,"
            "reverse,mobile,proxy,hosting,query"
        )

        session = await get_http_session()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return await msg.edit_text("<b>ERROR</b>\nFETCH_IP_FAILED")

            data = await resp.json()

        if data.get("status") != "success":
            return await msg.edit_text(
                f"<b>ERROR</b>\n<code>{html.escape(data.get('message', 'Unknown error'))}</code>",
                parse_mode="HTML"
            )

        text = (
            "<b>IP_INFORMATION</b>\n\n"
            f"<b>IP:</b> <code>{data.get('query')}</code>\n"
            f"<b>ISP:</b> {html.escape(data.get('isp','N/A'))}\n"
            f"<b>Org:</b> {html.escape(data.get('org','N/A'))}\n"
            f"<b>AS:</b> {html.escape(data.get('as','N/A'))}\n\n"

            "<b>LOCATION</b>\n"
            f"<b>Country:</b> {html.escape(data.get('country','N/A'))} ({data.get('countryCode','')})\n"
            f"<b>Region:</b> {html.escape(data.get('regionName','N/A'))}\n"
            f"<b>City:</b> {html.escape(data.get('city','N/A'))}\n"
            f"<b>ZIP:</b> {html.escape(data.get('zip','N/A'))}\n"
            f"<b>Coords:</b> {data.get('lat','N/A')}, {data.get('lon','N/A')}\n\n"

            "<b>TIMEZONE</b>\n"
            f"<b>TZ:</b> {html.escape(data.get('timezone','N/A'))}\n"
            f"<b>UTC Offset:</b> {data.get('offset','N/A')}\n\n"

            "<b>REVERSE_DNS:</b> {html.escape(data.get('reverse','N/A'))}\n"
            f"<b>Mobile:</b> {'Yes' if data.get('mobile') else 'No'}\n"
            f"<b>Proxy:</b> {'Yes' if data.get('proxy') else 'No'}\n"
            f"<b>Hosting:</b> {'Yes' if data.get('hosting') else 'No'}"
        )

        await msg.edit_text(text, parse_mode="HTML")

    except Exception as e:
        await msg.edit_text(
            f"<b>ERROR</b>\n<code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )
        

async def domain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    if not context.args:
        return await msg.reply_text(
            "<b>Usage:</b> .domain &lt;domain&gt;\n"
            "<b>Example:</b> .domain google.com",
            parse_mode="HTML"
        )

    domain = context.args[0]
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]

    if not re.match(r"^[\w.-]+$", domain) or domain.startswith("-"):
        return await msg.reply_text(
            "<b>ERROR</b>\nINVALID_DOMAIN_FORMAT",
            parse_mode="HTML"
        )

    loading = await msg.reply_text(
        f"Analyzing: <code>{html.escape(domain)}</code>...",
        parse_mode="HTML"
    )

    info = {}

    try:
        info["ip"] = socket.gethostbyname(domain)
    except Exception:
        info["ip"] = "N/A"

    try:
        w = whois.whois(domain)
        info["registrar"] = w.registrar or "N/A"
        info["created"] = str(w.creation_date) if w.creation_date else "N/A"
        info["expires"] = str(w.expiration_date) if w.expiration_date else "N/A"
        info["nameservers"] = w.name_servers or []
    except Exception:
        info["registrar"] = "N/A"
        info["created"] = "N/A"
        info["expires"] = "N/A"
        info["nameservers"] = []

    is_safe = False
    if info["ip"] != "N/A":
        try:
            ip = ipaddress.ip_address(info["ip"])
            if not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast):
                is_safe = True
        except ValueError:
            pass

    if not is_safe:
        if info["ip"] == "N/A":
            info["http_status"] = "N/A"
            info["server"] = "N/A"
        else:
            info["http_status"] = "Blocked (Unsafe IP)"
            info["server"] = "N/A"
    else:
        try:
            session = await get_http_session()
            async with session.get(
                f"http://{info['ip']}",
                headers={"Host": domain},
                timeout=aiohttp.ClientTimeout(total=10),
                allow_redirects=False
            ) as r:
                info["http_status"] = r.status
                info["server"] = r.headers.get("server", "N/A")
        except Exception:
            info["http_status"] = "N/A"
            info["server"] = "N/A"
        
    if info["nameservers"]:
        ns_text = "\n".join(
            f"• {html.escape(ns)}" for ns in info["nameservers"][:5]
        )
    else:
        ns_text = "N/A"

    text = (
        "<b>DOMAIN_INFO</b>\n\n"
        f"<b>Domain:</b> <code>{html.escape(domain)}</code>\n"
        f"<b>IP Address:</b> <code>{info['ip']}</code>\n"
        f"<b>HTTP Status:</b> <code>{info['http_status']}</code>\n"
        f"<b>Server:</b> <code>{html.escape(info['server'])}</code>\n\n"
        "<b>DETAILS</b>\n"
        f"<b>Registrar:</b> {html.escape(info['registrar'])}\n"
        f"<b>Created:</b> {html.escape(info['created'])}\n"
        f"<b>Expires:</b> {html.escape(info['expires'])}\n\n"
        "<b>NAME_SERVERS</b>\n"
        f"{ns_text}"
    )

    await loading.edit_text(text, parse_mode="HTML")