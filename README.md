# Telegram Enterprise Architecture Daemon

A high-performance Telegram Assistant engineered as a robust Unix control hub, dynamic code executor, wide-scale utility dispatcher, and persistent AI interface. The entire front-end has been rigorously restructured to eliminate visual gimmicks, establishing a cold, monochromatic aesthetic akin to native terminal operations.

## Core Infrastructure

The system runs on deep modifications of the asynchronous framework:
- **Asynchronous SQLite Pooling:** Block-free I/O architecture. Database connectors (System Settings, User Configs, Auto-DL toggles) are proxied through an `asyncio.to_thread` executor to sustain multi-group concurrent requests without stalling the main event loop.
- **Persistent AI Memory State:** Unlike conventional bots operating on volatile memory arrays, the LLMs leverage a dedicated SQLite ledger to house user interaction history. Utterly immune to amnesia caused by service restarts or hot-reload deployments (`$update`).

## "The Stoic Unix" Interface Standarization

All communicative outputs strictly adhere to a monochrome, emoji-free ANSI format, emulating the environment of a top-tier developer daemon:
- Precision-aligned block layouts using `<code>` syntax tags.
- Uppercase arrays for system logs (`[ DOWNLOAD PROTOCOL ]`, `[ SYSTEM CONFIGURATION ]`, etc).

## AI Engine Integration
- **`/ask`** — Anchored to Google Gemini 2.0 Flash for agile, dynamic logic and generic querying.
- **`/groq`** — Bound to Groq LLaMA-3 infrastructure, optimized for technical code breakdown and ultra-low latency computational reasoning.

## Network & Utility Workloads
1. **Remote Downloader (AutoDL):** Seamless URL detector powered by `yt-dlp`. Interprets media sources autonomously with native support for target audio conversions and unwatermarked extractions.
2. **Technical Utilities:** Features ultra-precise delay probing (`/ping`), IP geolocation (`/ip`), WHOIS Registry Indexing (`/whoisdomain`), and DNS extraction records (`/domain`).
3. **Multi-layer Environment:** Provides automated localization (`/tr`), compatibility modeling (`/ship`), and real-time forex indexing (`/kurs`).

## Advanced Shell Administration ($ Root Command)
Privileged access strictly gated through environments mapped by the asynchronous `OWNER_ID` parameter:
- **`$eval <kode>`** — Multi-line Python execution interpreter mapping runtime modules parallel to the bot's core memory. Standard libraries (`math`, `json`, `os`, `asyncio`, etc.) are persistently bound for immediate manipulation without repetitive imports.
- **`$sh <kode>`** — PTY piped shell access routing native Linux terminal tasks (`apt`, `git`, `ls`, etc.) straight into the interactive chat window.
- **`$update` / `$hotreload`** — Background repository pulling mechanism triggering instant structural compilation with sub-second downtime.

---

## Environment Config (`.env`)
Clone or export the fundamental parameters on the system root prior to initialization:

| Variable | Security / Description |
| :--- | :--- |
| `BOT_TOKEN` | Identity routing credential granted by `@BotFather`. |
| `OWNER_ID` | Telegram Account UID mapped as root control authority. |
| `LOG_CHAT_ID` | Private terminal pipe for critical systemic traceback monitoring. |
| `GEMINI_API_KEY` | Google Cloud generic inferencing auth. |
| `GROQ_API_KEY` | Groq Cloud lightning inferencing auth. |

## Initialization Parameters

This engine expects an active Python 3.9+ environment and FFmpeg binaries mounted on the host (WSL / Ubuntu / CentOS / Termux):

```bash
# 1. Fetch System Core
git clone <repository_url> telebot
cd telebot

# 2. Virtual Environment Projection (Recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Mount Daemon
python bot.py
```
