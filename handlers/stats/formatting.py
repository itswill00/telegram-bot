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
        f"📊 <b>Struktur Perangkat Server</b>\n"
        f"<code>────────────────────────</code>\n"
        f"🖥 <b>Sistem Operasi</b>\n"
        f"• Host: <code>{sysi['hostname']}</code>\n"
        f"• OS/Kernel: <code>{sysi['os']} | {sysi['kernel']}</code>\n"
        f"• Uptime: <code>{sysi['uptime']}</code>\n\n"
        f"⚙️ <b>Performa Perangkat Keras</b>\n"
        f"• Prosesor: <code>{cpu['load']:.1f}%</code> (<code>{cpu['cores']} Core</code> | <code>{cpu['freq']}</code>)\n"
        f"• Memori RAM: <code>{humanize_bytes(ram['used'])} / {humanize_bytes(ram['total'])}</code> (<code>{ram['pct']:.1f}%</code>)\n"
        f"• Memori SWAP: <code>{swap_str}</code>\n"
        f"• Ruang DISK (/): <code>{humanize_bytes(disk['used'])} / {humanize_bytes(disk['total'])}</code> <i>(Sisa: {humanize_bytes(disk['free'])})</i>\n"
        f"• Jaringan I/O: Tunda RX <code>{humanize_bytes(net['rx'])}</code> | TX <code>{humanize_bytes(net['tx'])}</code>\n\n"
        f"🛠 <b>Lingkungan Pustaka (Runtime)</b>\n"
        f"• Python: <code>{sysi['python']}</code> | Node: <code>{runtime['node']}</code>\n"
        f"• yt-dlp: <code>{runtime['ytdlp']}</code> | PTB: <code>{runtime['ptb']}</code>\n"
        f"• aiohttp: <code>{runtime['aiohttp']}</code>"
    )