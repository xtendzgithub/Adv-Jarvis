"""
jarvis/gui/github_panel.py — Dedicated GitHub dashboard panel for J.A.R.V.I.S.
Provides a tabbed UI for repos, issues, PRs, commits, and file browsing.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from jarvis.gui.styles import *


class GitHubPanel(ttk.Frame):
    """Side panel with GitHub repo browser, issues, PRs, commits."""

    def __init__(self, parent, assistant, **kwargs):
        super().__init__(parent, **kwargs)
        self.assistant = assistant
        self.github    = assistant.github
        self._current_repo = tk.StringVar()
        self.configure(style="Panel.TFrame")
        self._build()

    def _build(self):
        # ── Title ─────────────────────────────────────────────────────────
        tk.Label(self, text="⬡  GITHUB CONTROL", font=FONT_HEAD,
                 fg=ACCENT, bg=PANEL).pack(fill="x", padx=8, pady=(8, 2))

        # ── Repo selector ──────────────────────────────────────────────────
        sel_frame = tk.Frame(self, bg=PANEL)
        sel_frame.pack(fill="x", padx=6, pady=4)
        tk.Label(sel_frame, text="Repo:", fg=TEXT, bg=PANEL,
                 font=FONT_LABEL).pack(side="left")
        self._repo_entry = tk.Entry(sel_frame, textvariable=self._current_repo,
                                    bg=BG, fg=ACCENT, insertbackground=ACCENT,
                                    font=FONT_MONO, width=22)
        self._repo_entry.pack(side="left", padx=4)
        tk.Button(sel_frame, text="▶", bg=PANEL, fg=ACCENT,
                  relief="flat", command=self._load_repo).pack(side="left")

        # ── Notebook tabs ──────────────────────────────────────────────────
        nb_style = ttk.Style()
        nb_style.configure("GH.TNotebook",        background=PANEL, borderwidth=0)
        nb_style.configure("GH.TNotebook.Tab",    background=BG, foreground=DIM,
                           font=FONT_LABEL, padding=[6, 3])
        nb_style.map("GH.TNotebook.Tab",
                     foreground=[("selected", ACCENT)],
                     background=[("selected", PANEL)])

        self._nb = ttk.Notebook(self, style="GH.TNotebook")
        self._nb.pack(fill="both", expand=True, padx=6, pady=4)

        self._tab_repos   = self._make_tab("Repos")
        self._tab_issues  = self._make_tab("Issues")
        self._tab_prs     = self._make_tab("PRs")
        self._tab_commits = self._make_tab("Commits")
        self._tab_files   = self._make_tab("Files")

        # ── Quick action buttons ───────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=PANEL)
        btn_frame.pack(fill="x", padx=6, pady=4)
        btns = [
            ("My Repos",      self._load_my_repos),
            ("New Repo",      self._create_repo_dialog),
            ("New Issue",     self._create_issue_dialog),
            ("Search",        self._search_dialog),
            ("AI Review PR",  self._ai_review_pr_dialog),
            ("Notifications", self._load_notifications),
        ]
        for i, (label, cmd) in enumerate(btns):
            tk.Button(btn_frame, text=label, command=cmd,
                      bg=BG, fg=ACCENT, relief="flat",
                      font=FONT_LABEL, padx=6, pady=3
                      ).grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=1)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # Status bar
        self._status = tk.Label(self, text="Ready", fg=DIM, bg=PANEL,
                                font=FONT_LABEL, anchor="w")
        self._status.pack(fill="x", padx=8, pady=(0, 4))

    def _make_tab(self, name: str) -> tk.Text:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text=name)
        sb = tk.Scrollbar(frame)
        sb.pack(side="right", fill="y")
        txt = tk.Text(frame, bg=BG, fg=TEXT, font=FONT_MONO,
                      yscrollcommand=sb.set, wrap="none",
                      relief="flat", state="disabled")
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)
        return txt

    def _write(self, widget: tk.Text, content: str, clear=True):
        widget.config(state="normal")
        if clear:
            widget.delete("1.0", "end")
        widget.insert("end", content + "\n")
        widget.config(state="disabled")

    def _set_status(self, msg: str):
        self._status.config(text=msg)
        self._status.update()

    # ── Loaders ───────────────────────────────────────────────────────────────
    def _load_repo(self):
        repo = self._current_repo.get().strip()
        if not repo:
            return
        self._set_status(f"Loading {repo}…")
        self._write(self._tab_issues,  self._fmt_issues(repo))
        self._write(self._tab_prs,     self._fmt_prs(repo))
        self._write(self._tab_commits, self._fmt_commits(repo))
        self._write(self._tab_files,   self._fmt_files(repo))
        self._set_status(f"Loaded: {repo}")

    def _load_my_repos(self):
        self._set_status("Fetching your repos…")
        repos = self.github.list_repos(limit=50)
        self._write(self._tab_repos, "\n".join(repos))
        self._set_status(f"Found {len(repos)} repos")

    def _load_notifications(self):
        self._set_status("Fetching notifications…")
        notes = self.github.list_notifications()
        lines = [f"[{n['reason']}] {n['repo']}  →  {n['subject']}" for n in notes]
        self._write(self._tab_repos, "\n".join(lines) or "No notifications.")
        self._set_status("Notifications loaded")

    # ── Formatters ────────────────────────────────────────────────────────────
    def _fmt_issues(self, repo: str) -> str:
        issues = self.github.list_issues(repo)
        if not issues:
            return "No open issues."
        return "\n".join(
            f"  #{i['number']:4}  [{i['state']}]  {i['title'][:60]}\n"
            f"          by {i['user']}  →  {i['url']}"
            for i in issues
        )

    def _fmt_prs(self, repo: str) -> str:
        prs = self.github.list_pull_requests(repo)
        if not prs:
            return "No open pull requests."
        return "\n".join(
            f"  #{p['number']:4}  [{p['state']}]  {p['title'][:55]}\n"
            f"          {p['head']} → {p['base']}  by {p['user']}"
            for p in prs
        )

    def _fmt_commits(self, repo: str) -> str:
        commits = self.github.list_commits(repo)
        if not commits:
            return "No commits found."
        return "\n".join(
            f"  {c['sha'][:7]}  {c['date']}  {c['author'][:15]:<15}  {c['message'][:50]}"
            for c in commits
        )

    def _fmt_files(self, repo: str, path: str = "") -> str:
        files = self.github.list_files(repo, path)
        return "\n".join(files) or "Empty directory."

    # ── Dialogs ───────────────────────────────────────────────────────────────
    def _create_repo_dialog(self):
        name = simpledialog.askstring("New Repository", "Repository name:")
        if not name:
            return
        private = messagebox.askyesno("Visibility", "Make repo private?")
        result  = self.github.create_repo(name, private=private)
        self._write(self._tab_repos, result, clear=False)
        self.assistant.speak(result)

    def _create_issue_dialog(self):
        repo = self._current_repo.get().strip()
        if not repo:
            repo = simpledialog.askstring("Create Issue", "Repository (owner/repo):")
        if not repo:
            return
        title = simpledialog.askstring("Create Issue", f"Issue title for {repo}:")
        if not title:
            return
        body = simpledialog.askstring("Create Issue", "Issue body (optional):", initialvalue="")
        result = self.github.create_issue(repo, title, body or "")
        self._write(self._tab_issues, result, clear=False)
        self.assistant.speak(result)

    def _search_dialog(self):
        query = simpledialog.askstring("Search GitHub", "Search repositories:")
        if not query:
            return
        self._set_status(f"Searching for '{query}'…")
        repos = self.github.search_repos(query)
        lines = [
            f"⭐{r['stars']:<6}  {r['full_name']:<40}  {r['description'][:50]}"
            for r in repos
        ]
        self._write(self._tab_repos, "\n".join(lines) or "No results.")
        self._set_status(f"Found {len(repos)} results")

    def _ai_review_pr_dialog(self):
        repo = self._current_repo.get().strip()
        if not repo:
            repo = simpledialog.askstring("AI PR Review", "Repository:")
        if not repo:
            return
        num = simpledialog.askinteger("AI PR Review", "Pull Request number:")
        if not num:
            return
        self._set_status(f"Analysing PR #{num}…")
        review = self.github.ai_review_pr(repo, num, self.assistant.brain)
        self._write(self._tab_prs, f"\n=== AI Review of PR #{num} ===\n{review}")
        self._set_status("AI review complete")

    # ── Called by assistant for voice-triggered dialogs ───────────────────────
    def open_create_issue_dialog(self, repo: str):
        self._current_repo.set(repo)
        self._create_issue_dialog()
