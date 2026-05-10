"""
jarvis/system_control.py — OS-level operations for J.A.R.V.I.S.
Screenshots, app launching, system lock, weather API.
"""

import os
import platform
import subprocess
import datetime
import requests

import config


class SystemControl:
    """Handles OS-level actions and external APIs."""

    def __init__(self):
        self.os_name = platform.system()  # "Windows", "Darwin", "Linux"
        print(f"[System] OS detected: {self.os_name}")

    # ── Screenshot ────────────────────────────────────────────────────────────
    def take_screenshot(self) -> str:
        try:
            import pyautogui
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join("data", f"screenshot_{ts}.png")
            os.makedirs("data", exist_ok=True)
            pyautogui.screenshot().save(path)
            return path
        except Exception as e:
            return f"Screenshot error: {e}"

    # ── Application Launcher ──────────────────────────────────────────────────
    def open_app(self, app_name: str) -> str:
        app_map = {
            "notepad"        : {"Windows": "notepad",   "Darwin": "TextEdit"},
            "calculator"     : {"Windows": "calc",      "Darwin": "Calculator"},
            "browser"        : {"Windows": "chrome",    "Darwin": "Google Chrome"},
            "file explorer"  : {"Windows": "explorer",  "Darwin": "Finder"},
            "terminal"       : {"Windows": "cmd",       "Darwin": "Terminal",   "Linux": "x-terminal-emulator"},
            "vs code"        : {"Windows": "code",      "Darwin": "code",       "Linux": "code"},
            "spotify"        : {"Windows": "spotify",   "Darwin": "Spotify"},
        }
        for key, cmds in app_map.items():
            if key in app_name:
                cmd = cmds.get(self.os_name, "")
                if cmd:
                    if self.os_name == "Darwin":
                        subprocess.Popen(["open", "-a", cmd])
                    elif self.os_name == "Linux":
                        subprocess.Popen([cmd])
                    else:
                        os.system(cmd)
                    return f"Opening {key}"
        return f"App '{app_name}' not found in launcher list"

    # ── System Lock ───────────────────────────────────────────────────────────
    def lock(self):
        if self.os_name == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif self.os_name == "Darwin":
            os.system("pmset displaysleepnow")
        else:
            os.system("gnome-screensaver-command -l")

    # ── Shutdown / Restart ────────────────────────────────────────────────────
    def shutdown(self, restart: bool = False) -> str:
        if self.os_name == "Windows":
            os.system("shutdown /r /t 5" if restart else "shutdown /s /t 5")
        elif self.os_name == "Darwin":
            os.system("sudo shutdown -r now" if restart else "sudo shutdown -h now")
        else:
            os.system("sudo reboot" if restart else "sudo poweroff")
        return "System shutting down..."

    # ── Weather ───────────────────────────────────────────────────────────────
    def get_weather(self, query: str = "") -> str:
        if not config.OPENWEATHER_API_KEY:
            return "Weather API key not set. Add OPENWEATHER_API_KEY to .env"
        # Extract city from query
        city = config.DEFAULT_CITY
        for word in ["weather in", "temperature in", "forecast for"]:
            if word in query:
                city = query.split(word)[-1].strip().split()[0].title()
                break
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={config.OPENWEATHER_API_KEY}&units=metric"
            )
            data = requests.get(url, timeout=5).json()
            if data.get("cod") != 200:
                return f"Weather not found for '{city}'"
            temp  = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            desc  = data["weather"][0]["description"].title()
            humid = data["main"]["humidity"]
            wind  = data["wind"]["speed"]
            return (
                f"🌤 Weather in {city}:\n"
                f"   Condition : {desc}\n"
                f"   Temp      : {temp}°C (feels like {feels}°C)\n"
                f"   Humidity  : {humid}%\n"
                f"   Wind      : {wind} m/s"
            )
        except Exception as e:
            return f"Weather error: {e}"

    # ── System Info ───────────────────────────────────────────────────────────
    def get_system_info(self) -> str:
        try:
            import psutil
            cpu  = psutil.cpu_percent(interval=1)
            ram  = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return (
                f"💻 System Status:\n"
                f"   CPU Usage  : {cpu}%\n"
                f"   RAM        : {ram.percent}% used  "
                f"({ram.used // 1024**3}GB / {ram.total // 1024**3}GB)\n"
                f"   Disk       : {disk.percent}% used  "
                f"({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)"
            )
        except ImportError:
            import shutil
            total, used, _ = shutil.disk_usage("/")
            return (
                f"OS: {platform.system()} {platform.release()}\n"
                f"Disk: {used // 1024**3}GB / {total // 1024**3}GB used"
            )
