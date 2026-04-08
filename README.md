# Axon (Technical AI Assistant)

A high-performance Unix-style Telegram bot engineered for technical operations, administrative automation, and AI integration. Zero gimmick. Cold technical aesthetic.

---

## ARCHITECTURE
| Layer | Specification |
| :--- | :--- |
| **Runtime** | Python 3.12+ (Asynchronous / uvloop) |
| **Logic** | Custom-built event loop / python-telegram-bot |
| **Database** | aiosqlite (Persistent local state) |
| **AI Stack** | Gemini-2.0-Flash / Groq-Llama-3 (Distributed) |

---

## CORE_FEATURES

### AI_MODELS
- **LOGIC_ENGINE**: Google Gemini 2.0 Flash + Groq LLaMA-3.
- **STATE_MEMORY**: Conversational persistence across process cycles.
- **DATA_RAG**: Contextual document retrieval for grounded AI responses.

### MEDIA_TOOLS
- **UNIVERSAL_LOADER**: YouTube (4K/MP3), TikTok (No-Watermark), IG, X, and 100+ others via yt-dlp.
- **AUTODL_ENGINE**: Background link detection and parsing in group nodes.
- **LOCAL_BOT_API**: 2GB file overhead bypass via local host integration.

### SYSTEM_UTILITIES
- **NET_DIAGNOSTICS**: Latency probing, IP Geolocation, DNS extraction, and WHOIS.
- **WEATHER_REPORT**: Professional metrics for any global coordinate.
- **TECHNICAL_TR**: Zero-pleasantry cross-language translation.

---

## USER_DOCUMENTATION

| Command | Endpoint | Function |
| :--- | :--- | :--- |
| `.ask` | `Gemini` | Reasoning & Search |
| `.groq` | `Groq` | Technical Logic / Code |
| `.dl` | `ytdlp` | Media Acquisition |
| `.tr` | `API` | Translation |
| `.ping` | `Local` | Network Latency |
| `.stats` | `System` | Hardware Analytics |
| `.weather`| `API` | Global Metrics |

---

## ADMIN_INTERFACE ($ Mode)

Privileged commands restricted to **Owner ID** only.

### NODE_CONTROL ($node)
| Command | Parameter | Effect |
| :--- | :--- | :--- |
| `$node` | `status` | View global heartbeat & active modules |
| `$node` | `maintenance` | Toggle Owner-only mode (On/Off) |
| `$node` | `ai` | Toggle global AI availability (On/Off) |
| `$node` | `backup` | Execute database backup routine |
| `$node` | `logs` | Remote technical log monitoring |

### DEV_TOOLS
| Cmd | Function |
| :--- | :--- |
| `$core` | System dashboard (Inline keyboard) |
| `$py` | Execute Python in live runtime |
| `$sh` | Native shell / WSL interaction |
| `$cfg` | Environment configuration suite |
| `$live` | Toggle Watchdog (Auto-reboot on change) |
| `$sync` | Force repository synchronization |
| `$reboot`| Force-kill and respawn process |

### MODERATION_OPS
- `$purge / $revive`: Permanent ban / Unban operation.
- `$hush / $speak`: Mute / Unmute restriction.
- `$grant / $revoke`: Sudoer privilege management.

---

## DEPLOYMENT

### ENVIRONMENT_SETUP
1. **Clone**: `git clone https://github.com/itswill00/telegram-bot.git`
2. **Venv**: `python3 -m venv .venv && source .venv/bin/activate`
3. **Install**: `pip install -r requirements.txt`
4. **Config**: `cp .example.env .env`
5. **Run**: `python main.py`

### SCHEMA (.env)
```ini
BOT_TOKEN=781XXXXXXXX:XXXX...
OWNER_ID=123456789
GEMINI_API_KEY=AIzaSyA...
GROQ_API_KEY=gsk_...
LOCAL_BOT_API_HOST=127.0.0.1
```

---

## MISC
Licensed under GNU General Public License v3.0.

**Developer: @HirohitoKiyoshi**
