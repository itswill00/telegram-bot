# Axon (Technical AI Assistant)

A high-performance Telegram Bot designed as a Unix-style control hub, code executor, utility suite, and AI interface. Built with an asynchronous architecture for low-latency response cycles.

---

## CORE_FEATURES

### AI_MODELS
- **Gemini**: Google Gemini 2.0 Flash for web-integrated reasoning.
- **Groq**: Groq LLaMA-3 for high-speed technical/computational logic.
- **AUTO_FAILOVER**: Automatic provider switching during quota exhaustion.
- **RAG**: Local markdown ingestion for context-aware responses.
- **MEMORY**: Persistent conversational history via SQLite.

### MEDIA_TOOLS
- **UNIVERSAL_DL**: Download support for TikTok, YouTube (4K/MP3), Instagram, X/Twitter, and 100+ platforms via yt-dlp.
- **AUTODL**: Passive link detection and processing in groups.
- **LARGE_FILE_SUPPORT**: Bypasses 50MB limit up to 2GB via Local Bot API.

### SYSTEM_UTILITIES
- **DIAGNOSTICS**: Latency measurement (.ping), IP lookup (.ip), WHOIS indexing, and DNS extraction (.domain).
- **WEATHER**: Real-time reports for global locations (.weather).
- **TRANSLATOR**: Technical and formal cross-language translation (.tr).

---

## USER_DOCUMENTATION

Standard commands for all users:

| Command | Description | Example |
| :--- | :--- | :--- |
| .ask <query> | Query Gemini (Web-enabled) | .ask current BTC price |
| .groq <query> | Query Groq (Code/Logic) | .groq BFS algorithm in C++ |
| .dl <url> | Download media from link | .dl https://tiktok.com/... |
| .tr <text> | Translate text | .tr Good morning |
| .weather <loc> | Fetch weather data | .weather Jakarta |
| .ip <addr> | IP Geolocation scan | .ip 8.8.8.8 |
| .stats | System performance stats | .stats |

---

## ADMIN_ACCESS ($ Mode)

Privileged commands restricted to the Owner:

### NODE_CONTROL ($node)
- $node status: System module status.
- $node maintenance on|off: Owner-only mode toggle.
- $node ai on|off: Global AI toggle.
- $node backup on|off: Scheduled DB backup (12h).

### DEV_TOOLS
- $py <code>: Execute Python in live runtime.
- $sh <cmd>: Execute Linux/WSL shell commands.
- $sync: Pull repo changes and hot-reload.
- $reboot: Force process restart.
- $cfg: View environment configuration (Redacted).

---

## INSTALLATION

### PREREQUISITES
- Python 3.12+
- FFmpeg
- WSL / Linux (Ubuntu/Debian)

### SETUP
```bash
# 1. Clone Repo
git clone https://github.com/itswill00/telegram-bot.git telebot
cd telebot

# 2. Virtual Env
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Config
cp .example.env .env
# Edit .env with credentials

# 5. Execute
python main.py
```

### PARAMETERS (.env)
- BOT_TOKEN: Telegram Bot Token.
- OWNER_ID: Owner account UID.
- GEMINI_API_KEY: Google Cloud API Key.
- GROQ_API_KEY: Groq Cloud API Key.
- LOCAL_BOT_API_HOST: Local API endpoint (Default: 127.0.0.1).

---

## MISC
Licensed under GNU General Public License v3.0.

**Developer: @HirohitoKiyoshi**
