"""
jarvis/gui/styles.py — Centralized style constants for the J.A.R.V.I.S. GUI.
Dark cyber theme with green accent.
"""

import config

# ── Color palette ─────────────────────────────────────────────────────────────
BG           = config.BG_COLOR      # "#090909"
PANEL        = config.PANEL_COLOR   # "#111111"
ACCENT       = config.THEME_COLOR   # "#00ff88"
BLUE         = config.ACCENT_COLOR  # "#00aaff"
RED          = config.WARN_COLOR    # "#ff4444"
YELLOW       = "#ffcc00"
TEXT         = "#dddddd"
DIM          = "#555555"
CHAT_BG      = "#0c0c0c"

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_MONO    = ("Consolas",   10)
FONT_MONO_LG = ("Consolas",   12)
FONT_TITLE   = ("Arial",      22, "bold")
FONT_HEAD    = ("Arial",      13, "bold")
FONT_LABEL   = ("Consolas",    9)

# ── Chat tag colours ──────────────────────────────────────────────────────────
CHAT_TAGS = {
    "JARVIS" : ACCENT,
    "You"    : BLUE,
    "GITHUB" : YELLOW,
    "CODE"   : "#ff88cc",
    "System" : DIM,
    "ERROR"  : RED,
}
