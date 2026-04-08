# Axon (Technical AI Assistant)

A high-performance Unix-style Telegram bot engineered for technical operations, administrative automation, and AI integration. Zero gimmick. Cold technical aesthetic.

---

## ARCHITECTURE
| Layer | Specification |
| :--- | :--- |
| **Runtime** | Python 3.12+ (Asynchronous) |
| **Logic** | custom-built event loop / python-telegram-bot |
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

## ADMIN_ACCESS ($ Mode)

Privileged commands restricted to **Owner ID** only.

### NODE_CONTROL ($node)
| Command | Parameter | Effect |
| :--- | :--- | :--- |
| `$node` | `status` | View global heartbeat & active modules |
| `$node` | `maintenance` | Toggle Owner-only mode (On/Off) |
| `$node` | `ai` | Toggle global AI availability (On/Off) |
| `$node` | `backup` | Execute database backup routine |

### ENGINEERING_SUITE
- `$py <code>`: Execute Python logic in live runtime environments.
- `$sh <cmd>`: Direct Linux/WSL shell interaction.
- `$reboot`: Force process termination and state-persistent respawn.
- `$sync`: Synchronize repository with origin and hot-reload changes.
- `$cfg`: Redacted inspection of active environment parameters.

---

## DEPLOYMENT

### ENVIRONMENT_SETUP
1. **Clone**: `git clone https://github.com/itswill00/telegram-bot.git`
2. **Venv**: `python3 -m venv .venv && source .venv/bin/activate`
3. **Install**: `pip install -r requirements.txt`
4. **Config**: `cp .example.env .env` (Add credentials)
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
