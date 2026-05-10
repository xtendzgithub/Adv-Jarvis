"""
config.py — Central configuration for J.A.R.V.I.S.
All API keys and settings are loaded from environment variables (.env file).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── OpenAI / AI Brain ────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o")

# ─── GitHub ───────────────────────────────────────────────────────────────────
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "")         # Personal Access Token
GITHUB_USER    = os.getenv("GITHUB_USERNAME", "")      # Your GitHub username

# ─── Wolfram Alpha ────────────────────────────────────────────────────────────
WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "")

# ─── Weather ──────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
DEFAULT_CITY        = os.getenv("DEFAULT_CITY", "Mumbai")

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", "587"))

# ─── Database ─────────────────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "data/jarvis_memory.db")

# ─── TTS Settings ─────────────────────────────────────────────────────────────
TTS_RATE   = int(os.getenv("TTS_RATE", "175"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))
TTS_VOICE  = os.getenv("TTS_VOICE", "female")   # "male" or "female"

# ─── GUI Settings ─────────────────────────────────────────────────────────────
WINDOW_TITLE  = "J.A.R.V.I.S. — GitHub Intelligence System"
WINDOW_WIDTH  = 1400
WINDOW_HEIGHT = 850
THEME_COLOR   = "#00ff88"
BG_COLOR      = "#090909"
PANEL_COLOR   = "#111111"
ACCENT_COLOR  = "#00aaff"
WARN_COLOR    = "#ff4444"
