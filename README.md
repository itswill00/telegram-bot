# Axon (Enterprise AI Assistant)

A high-performance Telegram Bot engineered as a robust Unix control hub, dynamic code executor, wide-scale utility dispatcher, and persistent AI interface. Built with a pure asynchronous architecture for maximum scalability and low-latency response cycles.

---

## Core Features

### Advanced AI Integration
- **Hybrid AI Engine**: Leverages Google Gemini 2.0 Flash for web-integrated reasoning and Groq LLaMA-3 for high-speed technical/computational logic.
- **Failover Mechanism**: Automatically switches between AI providers during quota exhaustion or service outages.
- **RAG (Retrieval-Augmented Generation)**: Capable of ingesting local markdown documentation to provide context-aware responses.
- **Persistent AI Memory**: Conversational history is maintained across service restarts via highly optimized SQLite ledgers.

### High-Speed Media Acquisition
- **Universal Downloader**: Integrated support for TikTok (no watermark), YouTube (4K/MP3), Instagram (Reels/Stories), X/Twitter, and 100+ platforms via yt-dlp and gallery-dl.
- **Automated Pipeline (AutoDL)**: Passive link detection in groups for scheduled or instant acquisition.
- **Local Bot API Support**: Bypasses Telegram's 50MB limit, allowing uploads of up to 2GB via local server integration.

### Network & System Utilities
- **Technical Probing**: Precision-latency measurement (/ping), IP Geolocation (/ip), WHOIS Registry indexing, and DNS record extraction (/domain).
- **Meteorological Data**: Real-time professional weather reports for any global node.
- **Technical Localization**: Accurate cross-language translation with professional formatting.

---

## User Documentation

General commands accessible to all registered nodes:

| Command | Description | Example |
| :--- | :--- | :--- |
| .ask <query> | Query the AI engine (Web-enabled) | .ask what is the current BTC price? |
| .groq <query> | Query the Groq engine (Pure logic/code) | .groq write a BFS algorithm in C++ |
| .dl <url> | Process media acquisition from link | .dl https://tiktok.com/... |
| .tr <text> | Execute professional translation | .tr Good morning |
| .weather <loc> | Fetch meteorological report | .weather Jakarta |
| .ip <addr> | Perform IP Geolocation scan | .ip 8.8.8.8 |
| .stats | View system performance metrics | .stats |


---

## Owner Administration ($ Root Access)

Privileged commands restricted to the root architect:

### System Control Panel ($sys)
- $sys status: Monitor all active system modules.
- $sys maintenance on|off: Restrict bot responses to the owner only.
- $sys ai on|off: Toggle global AI availability.
- $sys backup on|off: Schedule automated 12h database backup routines.

### Engineering Tools
- $eval <python>: Execute Python code directly into the live runtime.
- $sh <command>: Execute native Linux/WSL shell commands.
- $update: Pull latest repository changes and synchronize structural logic.
- $restart: Force-kill and respawn the bot process.
- $env: Inspect environment mapping (critical secrets redacted).

---

## Technical Initialization

### System Prerequisites
- Python 3.12+
- FFmpeg (Media processing binaries)
- WSL (on Windows) or Linux (Ubuntu/Debian)

### Installation Sequence
```bash
# 1. Fetch Core Repository
git clone https://github.com/itswill00/telegram-bot.git telebot
cd telebot

# 2. Project Projection (Virtual Environment)
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependency Alignment
pip install -r requirements.txt

# 4. Environment Configuration
cp .example.env .env
# Edit .env with your credentials

# 5. Core Execution
python main.py
```

### Environment Parameters (.env)
- BOT_TOKEN: Telegram Identity Token.
- OWNER_ID: Account UID for root authority.
- GEMINI_API_KEY: Google Cloud auth.
- GROQ_API_KEY: Groq Cloud auth.
- LOCAL_BOT_API_HOST: Local API endpoint (Default: 127.0.0.1).

---

## Metadata
Proyect governed under the GNU General Public License v3.0. Developed for high-performance productivity and automation.

**Architect: @HirohitoKiyoshi**
