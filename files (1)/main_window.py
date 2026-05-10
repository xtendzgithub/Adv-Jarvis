"""
jarvis/gui/main_window.py — Main application window for J.A.R.V.I.S.
Cyber-dark theme with live camera, chat panel, and GitHub sidebar.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
import threading
import datetime

import config
from jarvis.gui.styles import *
from jarvis.gui.github_panel import GitHubPanel


class MainWindow:
    """The main Tkinter window — wires together all GUI panels."""

    def __init__(self, assistant):
        self.assistant = assistant
        self.root      = tk.Tk()
        self._camera_active = False
        self._cap           = None
        self._build_window()

    # ── Setup ─────────────────────────────────────────────────────────────────
    def _build_window(self):
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        # Style
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame",       background=BG)
        s.configure("Panel.TFrame", background=PANEL)
        s.configure("TButton",      background=PANEL, foreground=ACCENT,
                    font=FONT_LABEL, relief="flat")
        s.map("TButton", background=[("active", BG)])
        s.configure("TLabel",       background=BG, foreground=TEXT, font=FONT_MONO)

        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG, height=56)
        hdr.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(hdr, text="J.A.R.V.I.S.", font=FONT_TITLE,
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(hdr, text="GitHub Intelligence System",
                 font=FONT_LABEL, fg=DIM, bg=BG).pack(side="left", padx=12, pady=8)

        # Status indicators
        ind_frame = tk.Frame(hdr, bg=BG)
        ind_frame.pack(side="right")

        self._voice_ind  = self._indicator(ind_frame, "🎤 Voice",  RED)
        self._camera_ind = self._indicator(ind_frame, "📷 Camera", RED)
        self._gh_ind     = self._indicator(
            ind_frame,
            f"⬡  GitHub: @{self.assistant.github._user.login if self.assistant.github.connected else 'disconnected'}",
            ACCENT if self.assistant.github.connected else RED
        )

    def _indicator(self, parent, text, color) -> tk.Label:
        lbl = tk.Label(parent, text=text, fg=color, bg=BG, font=FONT_LABEL)
        lbl.pack(side="left", padx=8)
        return lbl

    def _build_body(self):
        body = tk.PanedWindow(self.root, bg=BG, sashwidth=4,
                              sashrelief="flat", orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=8)

        # ── LEFT: camera + quick actions ──────────────────────────────────────
        left = tk.Frame(body, bg=PANEL, width=380)
        body.add(left, minsize=300)

        # Camera feed
        self._cam_lbl = tk.Label(left, bg="black", width=50, height=16)
        self._cam_lbl.pack(padx=6, pady=6)

        cam_ctrl = tk.Frame(left, bg=PANEL)
        cam_ctrl.pack(fill="x", padx=6)
        self._cam_btn = tk.Button(cam_ctrl, text="▶ Start Camera",
                                   command=self._toggle_camera,
                                   bg=BG, fg=ACCENT, font=FONT_LABEL, relief="flat")
        self._cam_btn.pack(side="left", padx=4)
        tk.Button(cam_ctrl, text="👤 Add Face",
                  command=self._add_face_dialog,
                  bg=BG, fg=BLUE, font=FONT_LABEL, relief="flat").pack(side="left", padx=4)

        # Quick actions
        tk.Label(left, text="QUICK ACTIONS", fg=DIM, bg=PANEL,
                 font=FONT_LABEL).pack(anchor="w", padx=8, pady=(10, 2))
        actions = [
            ("🌐  Web Search",      lambda: self.assistant.process_command("search")),
            ("🌤  Weather",         lambda: self.assistant.process_command("weather")),
            ("💻  System Info",     self._show_system_info),
            ("📸  Screenshot",      lambda: self.assistant.process_command("screenshot")),
            ("🤖  Code Editor",     lambda: self.assistant.system.open_app("vs code")),
            ("🔒  Lock System",     lambda: self.assistant.process_command("lock")),
            ("🧠  Clear AI Memory", lambda: self.assistant.brain.clear_history() or
                                            self.display_message("System", "AI memory cleared.")),
        ]
        for label, cmd in actions:
            tk.Button(left, text=label, command=cmd, anchor="w",
                      bg=BG, fg=TEXT, font=FONT_LABEL,
                      relief="flat", padx=12, pady=5
                      ).pack(fill="x", padx=6, pady=1)

        # ── CENTRE: Chat ──────────────────────────────────────────────────────
        centre = tk.Frame(body, bg=BG)
        body.add(centre, minsize=380)

        tk.Label(centre, text="CHAT INTERFACE", fg=DIM, bg=BG,
                 font=FONT_LABEL).pack(anchor="w", padx=8)

        self._chat = scrolledtext.ScrolledText(
            centre, bg=CHAT_BG, fg=TEXT, font=FONT_MONO,
            insertbackground=ACCENT, relief="flat",
            state="disabled", wrap="word"
        )
        self._chat.pack(fill="both", expand=True, padx=6, pady=4)

        # Configure chat tags
        for sender, color in CHAT_TAGS.items():
            self._chat.tag_config(sender, foreground=color)
        self._chat.tag_config("timestamp", foreground=DIM)

        # Input row
        inp_frame = tk.Frame(centre, bg=BG)
        inp_frame.pack(fill="x", padx=6, pady=(0, 4))

        self._input = tk.Entry(inp_frame, bg="#1a1a1a", fg=ACCENT,
                               insertbackground=ACCENT, font=FONT_MONO_LG,
                               relief="flat")
        self._input.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 4))
        self._input.bind("<Return>", self._on_enter)

        tk.Button(inp_frame, text="SEND",    command=self._on_enter,
                  bg=ACCENT, fg=BG, font=FONT_HEAD, relief="flat", padx=12
                  ).pack(side="right", padx=2)
        tk.Button(inp_frame, text="🎤",      command=self._start_voice,
                  bg=PANEL, fg=ACCENT, font=FONT_HEAD, relief="flat", padx=8
                  ).pack(side="right")

        # ── RIGHT: GitHub panel ───────────────────────────────────────────────
        right = tk.Frame(body, bg=PANEL, width=380)
        body.add(right, minsize=300)

        self.github_panel = GitHubPanel(right, self.assistant, style="Panel.TFrame")
        self.github_panel.pack(fill="both", expand=True)

    def _build_statusbar(self):
        self._statusbar = tk.Label(
            self.root, text="J.A.R.V.I.S. online  •  Ready",
            fg=DIM, bg="#050505", anchor="w", font=FONT_LABEL
        )
        self._statusbar.pack(fill="x", side="bottom", ipadx=10, ipady=3)

    # ── Chat ──────────────────────────────────────────────────────────────────
    def display_message(self, sender: str, message: str):
        self._chat.config(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._chat.insert("end", f"[{ts}] ", "timestamp")
        self._chat.insert("end", f"{sender}: ", sender)
        self._chat.insert("end", f"{message}\n\n")
        self._chat.config(state="disabled")
        self._chat.see("end")

    def _on_enter(self, event=None):
        text = self._input.get().strip()
        if not text:
            return
        self.display_message("You", text)
        self._input.delete(0, "end")
        threading.Thread(target=self.assistant.process_command,
                         args=(text,), daemon=True).start()

    # ── Voice ─────────────────────────────────────────────────────────────────
    def _start_voice(self):
        if not self.assistant.voice.stt_available:
            self.display_message("System", "Speech recognition not available.")
            return
        self._voice_ind.config(text="🎤 Listening…", fg=ACCENT)
        self._statusbar.config(text="Listening for voice input…")

        def listen_thread():
            text = self.assistant.voice.listen()
            self.root.after(0, lambda: self._voice_ind.config(text="🎤 Voice", fg=RED))
            self.root.after(0, lambda: self._statusbar.config(text="Ready"))
            if text:
                self.root.after(0, lambda: self.display_message("You", text))
                threading.Thread(target=self.assistant.process_command,
                                 args=(text,), daemon=True).start()
            else:
                self.root.after(0, lambda: self.display_message("System",
                                                                  "Could not understand audio."))

        threading.Thread(target=listen_thread, daemon=True).start()

    # ── Camera ────────────────────────────────────────────────────────────────
    def _toggle_camera(self):
        if not self._camera_active:
            self._start_camera()
        else:
            self._stop_camera()

    def _start_camera(self):
        try:
            import cv2
            self._cap = cv2.VideoCapture(0)
            self._camera_active = True
            self._cam_btn.config(text="⏹ Stop Camera")
            self._camera_ind.config(text="📷 Active", fg=ACCENT)
            self._update_camera()
        except ImportError:
            self.display_message("System", "opencv-python not installed.")

    def _stop_camera(self):
        self._camera_active = False
        if self._cap:
            self._cap.release()
        self._cam_btn.config(text="▶ Start Camera")
        self._camera_ind.config(text="📷 Camera", fg=RED)
        self._cam_lbl.config(image="")

    def _update_camera(self):
        if not self._camera_active or not self._cap or not self._cap.isOpened():
            return
        import cv2
        from PIL import Image, ImageTk
        ret, frame = self._cap.read()
        if ret:
            faces = self.assistant.faces.identify_faces(frame)
            frame = self.assistant.faces.draw_faces(frame, faces)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img   = Image.fromarray(rgb)
            img.thumbnail((360, 240))
            photo = ImageTk.PhotoImage(img)
            self._cam_lbl.imgtk = photo
            self._cam_lbl.configure(image=photo)
        self.root.after(33, self._update_camera)   # ~30 fps

    def _add_face_dialog(self):
        name = simpledialog.askstring("Add Face", "Enter name for this person:")
        if name and self._cap:
            result = self.assistant.faces.capture_face_from_camera(name, self._cap)
            self.display_message("System", result)
            self.assistant.speak(result)

    # ── Misc ──────────────────────────────────────────────────────────────────
    def _show_system_info(self):
        info = self.assistant.system.get_system_info()
        self.display_message("System", info)

    def open_create_issue_dialog(self, repo: str):
        self.github_panel.open_create_issue_dialog(repo)

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._stop_camera()
        if self.assistant.conn:
            self.assistant.conn.close()
        self.root.destroy()
