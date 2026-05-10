# ⬡ J.A.R.V.I.S. — GitHub Intelligence System v2.0

> **Just A Rather Very Intelligent System** — a modular AI desktop assistant with deep GitHub integration, voice control, face recognition, and GPT-4o powered intelligence.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| 🤖 **AI Brain** | GPT-4o chat, code generation, code review, PR summarisation |
| ⬡ **GitHub** | Repos, Issues, PRs, Commits, File browser, AI PR Review, Search, Fork, Star, Clone |
| 🎤 **Voice** | Wake word, speech-to-text, text-to-speech (natural voice) |
| 👤 **Face ID** | Real-time face recognition via webcam, add/remove faces |
| 💻 **System** | App launcher, screenshot, system info, lock, weather |
| 🖥️ **GUI** | Cyber-dark Tkinter GUI with live camera feed and tabbed GitHub panel |

---

## 📁 Project Structure

```
jarvis-ai/
├── main.py                         # Entry point
├── config.py                       # Central config (loads from .env)
├── requirements.txt
├── .env.example                    # Template — copy to .env
├── .gitignore
├── data/                           # SQLite DB + screenshots (gitignored)
└── jarvis/
    ├── __init__.py
    ├── assistant.py                # Core orchestrator
    ├── ai_brain.py                 # OpenAI GPT-4o wrapper
    ├── github_manager.py           # Full GitHub API (PyGithub)
    ├── voice_engine.py             # TTS + STT
    ├── face_recognition_module.py  # Face detect + identify
    ├── system_control.py           # OS controls + weather
    └── gui/
        ├── __init__.py
        ├── main_window.py          # Main Tkinter window
        ├── github_panel.py         # GitHub sidebar panel
        └── styles.py               # Color/font constants
```

---

## 🚀 Quick Start

### 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/jarvis-ai.git
cd jarvis-ai
```

### 2 — Create and activate a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

> **Note on `dlib` / `face_recognition` (Windows):**  
> Install a pre-built `dlib` wheel from [here](https://github.com/z-mahmud-ali/Dlib_Windows_Python3.x) before running `pip install face-recognition`.

### 4 — Configure API keys
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 5 — Run
```bash
python main.py
```

---

## 🔑 API Keys Required

| Service | Purpose | Get Key |
|---|---|---|
| **OpenAI** | GPT-4o chat + code gen | [platform.openai.com](https://platform.openai.com) |
| **GitHub PAT** | Full repo management | [github.com/settings/tokens](https://github.com/settings/tokens) |
| **OpenWeatherMap** | Weather queries | [openweathermap.org/api](https://openweathermap.org/api) |

> GitHub PAT required scopes: `repo`, `read:user`, `notifications`

---

## 🎤 Voice Commands (Examples)

| Say | Action |
|---|---|
| *"What time is it?"* | Current time |
| *"List my repos"* | Show all your GitHub repos |
| *"List issues for jarvis-ai"* | Open issues for a repo |
| *"Create issue for jarvis-ai"* | Open create-issue dialog |
| *"Search GitHub for machine learning"* | Search public repos |
| *"Show commits for jarvis-ai"* | Recent commit history |
| *"AI review PR 5 in jarvis-ai"* | GPT-4o PR code review |
| *"Write code for a binary search"* | Generate Python code |
| *"Weather in Pune"* | Current weather |
| *"Take a screenshot"* | Capture screen |
| *"Lock system"* | Lock workstation |

---

## 🖥️ GUI Layout

```
┌─────────────────────────────────────────────────────────┐
│  J.A.R.V.I.S.  GitHub Intelligence System         🎤 ⬡  │
├──────────────┬─────────────────────┬────────────────────┤
│  📷 Camera   │    CHAT INTERFACE   │  ⬡ GITHUB CONTROL  │
│  feed with   │                     │  ┌──────────────┐  │
│  face boxes  │  [00:00] JARVIS:    │  │ Repos Issues │  │
│              │  J.A.R.V.I.S. ...   │  │ PRs  Commits │  │
│  Quick       │                     │  │ Files        │  │
│  Actions:    │  [00:01] You:       │  └──────────────┘  │
│  🌐 Weather  │  list my repos      │  [New Repo]        │
│  💻 SysInfo  │                     │  [New Issue]       │
│  📸 Shot     │  ┌─────────────┐🎤  │  [AI Review PR]    │
│  🔒 Lock     │  │  type here  │▶  │  [Search]          │
└──────────────┴─────────────────────┴────────────────────┘
│  J.A.R.V.I.S. online  •  Ready                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **OpenAI GPT-4o** — AI brain & code generation
- **PyGithub** — GitHub API integration
- **pyttsx3** — Offline text-to-speech
- **SpeechRecognition + PyAudio** — Speech-to-text
- **face_recognition + dlib + OpenCV** — Real-time face ID
- **Pillow + pyautogui** — Image capture & GUI
- **SQLite** — Local memory database
- **Tkinter** — Desktop GUI

---

> *Built with ❤️ by J.A.R.V.I.S. — because every developer deserves their own AI co-pilot.*
