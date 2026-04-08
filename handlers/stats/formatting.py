def humanize_bytes(n: int) -> str:
    try:
        f = float(n)
    except Exception:
        return "N/A"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if f < 1024 or unit == "TB":
            return f"{f:.1f}{unit}"
        f /= 1024.0
    return f"{f:.1f}B"


def humanize_frequency(mhz):
    try:
        mhz = float(mhz)
    except Exception:
        return "N/A"
    if mhz >= 1000:
        return f"{mhz / 1000:.2f} GHz"
    return f"{mhz:.0f} MHz"


def shorten_text(text, limit=64):
    text = str(text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def clamp_percent(x):
    try:
        value = float(x)
    except Exception:
        return 0.0
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return value


def build_fallback_text(stats):
    cpu = stats["cpu"]
    ram = stats["ram"]
    swap = stats["swap"]
    disk = stats["disk"]
    net = stats["net"]
    sysi = stats["sys"]
    runtime = stats["runtime"]

    swap_str = f"{humanize_bytes(swap['used'])}/{humanize_bytes(swap['total'])} ({swap['pct']:.1f}%)" if swap["total"] else "N/A"

    return (
        f"<b>System Topology </b>\n"
        f"<b>Operating Environment </b>\n"
        f"• Host     : <code>{sysi['hostname']}</code>\n"
        f"• Kernel   : <code>{sysi['os']} | {sysi['kernel']}</code>\n"
        f"• Uptime   : <code>{sysi['uptime']}</code>\n\n"
        f"<b>Hardware Telemetry </b>\n"
        f"• CPU Load : <code>{cpu['load']:.1f}%</code> (<code>{cpu['cores']} Core</code> | <code>{cpu['freq']}</code>)\n"
        f"• Mem RAM  : <code>{humanize_bytes(ram['used'])} / {humanize_bytes(ram['total'])}</code> (<code>{ram['pct']:.1f}%</code>)\n"
        f"• Mem SWAP : <code>{swap_str}</code>\n"
        f"• Disk I/O : <code>{humanize_bytes(disk['used'])} / {humanize_bytes(disk['total'])}</code> <i>(Free: {humanize_bytes(disk['free'])})</i>\n"
        f"• Net I/O  : RX <code>{humanize_bytes(net['rx'])}</code> | TX <code>{humanize_bytes(net['tx'])}</code>\n\n"
        f"<b>Runtime Dependencies </b>\n"
        f"• Runtime  : Pyr <code>{sysi['python']}</code> | V8 <code>{runtime['node']}</code>\n"
        f"• Binaries : YTD <code>{runtime['ytdlp']}</code> | PTB <code>{runtime['ptb']}</code>\n"
        f"• Socket   : HTTP <code>{runtime['aiohttp']}</code>"
    )