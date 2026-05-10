"""
jarvis/assistant.py — Core orchestrator for J.A.R.V.I.S.
Wires together voice, AI brain, GitHub manager, system control, and GUI.
"""

import threading
import datetime
import sqlite3
import os

import config
from jarvis.voice_engine       import VoiceEngine
from jarvis.ai_brain           import AIBrain
from jarvis.github_manager     import GitHubManager
from jarvis.system_control     import SystemControl
from jarvis.face_recognition_module import FaceRecognitionModule
from jarvis.gui.main_window    import MainWindow


class JarvisAssistant:
    """Top-level assistant — initialises all subsystems and starts the GUI."""

    def __init__(self):
        os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)

        # ── Subsystems ────────────────────────────────────────────────────────
        self.voice   = VoiceEngine()
        self.brain   = AIBrain()
        self.github  = GitHubManager()
        self.system  = SystemControl()
        self.faces   = FaceRecognitionModule()

        # ── Persistent memory ─────────────────────────────────────────────────
        self.conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        self._init_db()

        # ── GUI (created last so subsystems are ready) ─────────────────────
        self.gui = MainWindow(assistant=self)

    # ── DB ────────────────────────────────────────────────────────────────────
    def _init_db(self):
        c = self.conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS commands (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                command_text  TEXT,
                intent        TEXT,
                timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS faces (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT UNIQUE,
                encoding   BLOB,
                image_path TEXT
            );
            CREATE TABLE IF NOT EXISTS github_cache (
                key        TEXT PRIMARY KEY,
                value      TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    # ── Public helpers used by GUI ─────────────────────────────────────────
    def speak(self, text: str):
        """Speak text aloud in a background thread."""
        self.gui.display_message("JARVIS", text)
        threading.Thread(target=self.voice.speak, args=(text,), daemon=True).start()

    def process_command(self, text: str):
        """Route a command string to the correct handler."""
        text_lower = text.lower().strip()
        self._save_command(text_lower)

        # ── GitHub commands ────────────────────────────────────────────────
        if any(w in text_lower for w in ["github", "repo", "repository", "commit",
                                          "issue", "pull request", "pr", "branch",
                                          "clone", "push", "fork"]):
            self._handle_github_command(text_lower)

        # ── Time / Date ───────────────────────────────────────────────────
        elif any(w in text_lower for w in ["time", "clock"]):
            self.speak(f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}")
        elif any(w in text_lower for w in ["date", "today"]):
            self.speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")

        # ── Web search ────────────────────────────────────────────────────
        elif any(w in text_lower for w in ["search", "google", "look up"]):
            import webbrowser
            query = text_lower.replace("search", "").replace("google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            self.speak(f"Searching for {query}")

        # ── Weather ───────────────────────────────────────────────────────
        elif any(w in text_lower for w in ["weather", "temperature", "forecast"]):
            self.speak(self.system.get_weather(text_lower))

        # ── Code generation ───────────────────────────────────────────────
        elif any(w in text_lower for w in ["write code", "generate code", "create code",
                                            "python script", "program"]):
            reply = self.brain.generate_code(text)
            self.speak("Code generated. Check the chat panel.")
            self.gui.display_message("CODE", reply)

        # ── Screenshot ────────────────────────────────────────────────────
        elif any(w in text_lower for w in ["screenshot", "capture screen"]):
            path = self.system.take_screenshot()
            self.speak(f"Screenshot saved as {path}")

        # ── Lock ──────────────────────────────────────────────────────────
        elif any(w in text_lower for w in ["lock", "secure"]):
            self.speak("Locking system. Goodbye.")
            self.system.lock()

        # ── Face ──────────────────────────────────────────────────────────
        elif any(w in text_lower for w in ["face", "who is", "recognise", "recognize"]):
            self.speak("Face recognition is active when camera is on.")

        # ── Fallback → AI Brain ───────────────────────────────────────────
        else:
            reply = self.brain.chat(text)
            self.speak(reply)

    # ── GitHub command dispatcher ──────────────────────────────────────────
    def _handle_github_command(self, text: str):
        result = ""

        if "list repo" in text or "my repos" in text or "show repos" in text:
            repos = self.github.list_repos()
            result = "Your repositories:\n" + "\n".join(f"  • {r}" for r in repos)

        elif "create repo" in text or "new repo" in text:
            # Extract name after "create repo <name>"
            parts = text.split("create repo")[-1].strip().split()
            name = parts[0] if parts else "jarvis-created-repo"
            private = "private" in text
            result = self.github.create_repo(name, private=private)

        elif "list issue" in text or "show issue" in text:
            repo_name = self._extract_repo_name(text)
            issues = self.github.list_issues(repo_name)
            result = f"Issues for {repo_name}:\n" + "\n".join(
                f"  #{i['number']} [{i['state']}] {i['title']}" for i in issues
            )

        elif "create issue" in text or "open issue" in text:
            repo_name = self._extract_repo_name(text)
            result = f"Opening create-issue dialog for {repo_name}…"
            self.gui.open_create_issue_dialog(repo_name)
            return

        elif "close issue" in text:
            repo_name = self._extract_repo_name(text)
            # Expect "close issue #42 in <repo>"
            num = self._extract_issue_number(text)
            result = self.github.close_issue(repo_name, num) if num else "Please specify issue number."

        elif "list pr" in text or "pull request" in text:
            repo_name = self._extract_repo_name(text)
            prs = self.github.list_pull_requests(repo_name)
            result = f"Pull Requests for {repo_name}:\n" + "\n".join(
                f"  #{p['number']} [{p['state']}] {p['title']}" for p in prs
            )

        elif "commit" in text:
            repo_name = self._extract_repo_name(text)
            commits = self.github.list_commits(repo_name)
            result = f"Recent commits for {repo_name}:\n" + "\n".join(
                f"  {c['sha'][:7]} — {c['message']} ({c['author']})" for c in commits[:10]
            )

        elif "branch" in text:
            repo_name = self._extract_repo_name(text)
            branches = self.github.list_branches(repo_name)
            result = f"Branches for {repo_name}:\n" + "\n".join(f"  • {b}" for b in branches)

        elif "search" in text and ("code" in text or "repo" in text):
            query = text.replace("search", "").replace("code", "").replace("repo", "").strip()
            repos = self.github.search_repos(query)
            result = f"Search results for '{query}':\n" + "\n".join(
                f"  ⭐{r['stars']}  {r['full_name']} — {r['description']}" for r in repos[:8]
            )

        elif "read file" in text or "show file" in text:
            repo_name = self._extract_repo_name(text)
            path = self._extract_file_path(text)
            content = self.github.get_file_content(repo_name, path)
            result = f"File: {path}\n\n{content}"

        elif "star" in text:
            repo_name = self._extract_repo_name(text)
            result = self.github.star_repo(repo_name)

        elif "fork" in text:
            repo_name = self._extract_repo_name(text)
            result = self.github.fork_repo(repo_name)

        elif "clone" in text:
            repo_name = self._extract_repo_name(text)
            dest = self._extract_clone_dest(text)
            result = self.github.clone_repo(repo_name, dest)

        elif "readme" in text:
            repo_name = self._extract_repo_name(text)
            result = self.github.get_readme(repo_name)

        elif "stats" in text or "insight" in text:
            repo_name = self._extract_repo_name(text)
            result = self.github.get_repo_stats(repo_name)

        else:
            # Unknown GitHub command → let AI brain interpret
            result = self.brain.chat(f"GitHub task: {text}")

        self.speak(result[:300])  # Read first 300 chars aloud
        self.gui.display_message("GITHUB", result)

    # ── Extraction helpers ─────────────────────────────────────────────────
    def _extract_repo_name(self, text: str) -> str:
        for kw in ["for repo", "for", "in repo", "in", "repo"]:
            if kw in text:
                after = text.split(kw)[-1].strip().split()[0]
                if after:
                    return after
        return ""

    def _extract_issue_number(self, text: str) -> int | None:
        import re
        m = re.search(r"#(\d+)", text)
        return int(m.group(1)) if m else None

    def _extract_file_path(self, text: str) -> str:
        for kw in ["file", "path"]:
            if kw in text:
                parts = text.split(kw)[-1].strip().split()
                if parts:
                    return parts[0]
        return "README.md"

    def _extract_clone_dest(self, text: str) -> str:
        if "to" in text:
            return text.split("to")[-1].strip().split()[0]
        return "."

    # ── DB ────────────────────────────────────────────────────────────────
    def _save_command(self, text: str):
        self.conn.execute("INSERT INTO commands (command_text) VALUES (?)", (text,))
        self.conn.commit()

    def run(self):
        self.speak("J.A.R.V.I.S. GitHub Intelligence System online. Ready, sir.")
        self.gui.start()
