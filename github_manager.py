"""
jarvis/github_manager.py — Full GitHub API integration for J.A.R.V.I.S.

Wraps PyGitHub to provide repo management, issues, PRs, commits,
file reading/writing, search, cloning, forking, and repo statistics.
"""

from __future__ import annotations

import os
import subprocess
import base64
from typing import List, Dict, Any

try:
    from github import Github, GithubException, Auth
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

import config


class GitHubManager:
    """All GitHub operations for J.A.R.V.I.S."""

    def __init__(self):
        self._gh  = None
        self._user = None
        self._connected = False
        self._connect()

    # ── Connection ────────────────────────────────────────────────────────────
    def _connect(self):
        if not GITHUB_AVAILABLE:
            print("[GitHub] PyGithub not installed. Run: pip install PyGithub")
            return
        if not config.GITHUB_TOKEN:
            print("[GitHub] No GITHUB_TOKEN set in .env")
            return
        try:
            auth = Auth.Token(config.GITHUB_TOKEN)
            self._gh  = Github(auth=auth)
            self._user = self._gh.get_user()
            self._connected = True
            print(f"[GitHub] Connected as @{self._user.login}")
        except Exception as e:
            print(f"[GitHub] Connection failed: {e}")

    @property
    def connected(self) -> bool:
        return self._connected

    def _require_connection(self):
        if not self._connected:
            return "GitHub not connected. Check your GITHUB_TOKEN in .env"
        return None

    def _get_repo(self, repo_name: str):
        """Resolve 'owner/repo' or 'repo' (defaults to authenticated user)."""
        if "/" in repo_name:
            return self._gh.get_repo(repo_name)
        return self._user.get_repo(repo_name)

    # ── Repository Operations ─────────────────────────────────────────────────
    def list_repos(self, limit: int = 30) -> List[str]:
        err = self._require_connection()
        if err:
            return [err]
        try:
            repos = list(self._user.get_repos())[:limit]
            return [f"{r.full_name}  [⭐{r.stargazers_count}]  {'🔒' if r.private else '🌍'}" for r in repos]
        except Exception as e:
            return [f"Error: {e}"]

    def create_repo(self, name: str, description: str = "Created by J.A.R.V.I.S.",
                    private: bool = False, init_readme: bool = True) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=init_readme,
            )
            return f"✅ Repo '{repo.full_name}' created → {repo.html_url}"
        except GithubException as e:
            return f"❌ GitHub error: {e.data.get('message', str(e))}"

    def delete_repo(self, repo_name: str) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._get_repo(repo_name)
            repo.delete()
            return f"🗑️  Repo '{repo_name}' deleted."
        except Exception as e:
            return f"Error: {e}"

    def get_repo_stats(self, repo_name: str) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            r = self._get_repo(repo_name)
            return (
                f"📦 {r.full_name}\n"
                f"   Description : {r.description or 'N/A'}\n"
                f"   Language    : {r.language or 'N/A'}\n"
                f"   ⭐ Stars    : {r.stargazers_count}\n"
                f"   🍴 Forks    : {r.forks_count}\n"
                f"   👁  Watchers : {r.watchers_count}\n"
                f"   Issues      : {r.open_issues_count} open\n"
                f"   Default Br. : {r.default_branch}\n"
                f"   Created     : {r.created_at.strftime('%Y-%m-%d')}\n"
                f"   Last Push   : {r.pushed_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"   URL         : {r.html_url}"
            )
        except Exception as e:
            return f"Error: {e}"

    def fork_repo(self, repo_name: str) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo   = self._get_repo(repo_name)
            forked = self._user.create_fork(repo)
            return f"🍴 Forked '{repo_name}' → {forked.html_url}"
        except Exception as e:
            return f"Error: {e}"

    def star_repo(self, repo_name: str) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._get_repo(repo_name)
            self._user.add_to_starred(repo)
            return f"⭐ Starred '{repo_name}'"
        except Exception as e:
            return f"Error: {e}"

    def clone_repo(self, repo_name: str, dest: str = ".") -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._get_repo(repo_name)
            clone_url = repo.clone_url
            result = subprocess.run(
                ["git", "clone", clone_url, dest],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return f"✅ Cloned '{repo_name}' to {os.path.abspath(dest)}"
            return f"❌ Clone failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"

    def search_repos(self, query: str, sort: str = "stars",
                     limit: int = 10) -> List[Dict[str, Any]]:
        err = self._require_connection()
        if err:
            return [{"full_name": err, "stars": 0, "description": ""}]
        try:
            results = self._gh.search_repositories(query=query, sort=sort)
            out = []
            for r in list(results)[:limit]:
                out.append({
                    "full_name"  : r.full_name,
                    "stars"      : r.stargazers_count,
                    "description": r.description or "",
                    "url"        : r.html_url,
                    "language"   : r.language or "",
                })
            return out
        except Exception as e:
            return [{"full_name": f"Error: {e}", "stars": 0, "description": ""}]

    # ── Branch Operations ─────────────────────────────────────────────────────
    def list_branches(self, repo_name: str) -> List[str]:
        err = self._require_connection()
        if err:
            return [err]
        try:
            repo = self._get_repo(repo_name)
            return [b.name for b in repo.get_branches()]
        except Exception as e:
            return [f"Error: {e}"]

    def create_branch(self, repo_name: str, branch: str, from_branch: str = "") -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._get_repo(repo_name)
            source = from_branch or repo.default_branch
            sha    = repo.get_branch(source).commit.sha
            repo.create_git_ref(ref=f"refs/heads/{branch}", sha=sha)
            return f"✅ Branch '{branch}' created from '{source}'"
        except Exception as e:
            return f"Error: {e}"

    # ── Commit Operations ─────────────────────────────────────────────────────
    def list_commits(self, repo_name: str, branch: str = "",
                     limit: int = 20) -> List[Dict[str, str]]:
        err = self._require_connection()
        if err:
            return [{"sha": "", "message": err, "author": ""}]
        try:
            repo = self._get_repo(repo_name)
            kwargs = {"sha": branch} if branch else {}
            commits = list(repo.get_commits(**kwargs))[:limit]
            return [{
                "sha"    : c.sha,
                "message": c.commit.message.split("\n")[0],
                "author" : c.commit.author.name,
                "date"   : c.commit.author.date.strftime("%Y-%m-%d"),
            } for c in commits]
        except Exception as e:
            return [{"sha": "", "message": f"Error: {e}", "author": ""}]

    # ── File Operations ───────────────────────────────────────────────────────
    def get_file_content(self, repo_name: str, path: str,
                         branch: str = "") -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo   = self._get_repo(repo_name)
            kwargs = {"ref": branch} if branch else {}
            content_file = repo.get_contents(path, **kwargs)
            decoded = base64.b64decode(content_file.content).decode("utf-8", errors="replace")
            return decoded
        except Exception as e:
            return f"Error reading file: {e}"

    def create_or_update_file(self, repo_name: str, path: str,
                              content: str, message: str,
                              branch: str = "") -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo   = self._get_repo(repo_name)
            kwargs = {"branch": branch} if branch else {}
            # Try update first, then create
            try:
                existing = repo.get_contents(path, **kwargs)
                repo.update_file(path, message, content, existing.sha, **kwargs)
                return f"✅ Updated '{path}' in '{repo_name}'"
            except Exception:
                repo.create_file(path, message, content, **kwargs)
                return f"✅ Created '{path}' in '{repo_name}'"
        except Exception as e:
            return f"Error: {e}"

    def list_files(self, repo_name: str, path: str = "",
                   branch: str = "") -> List[str]:
        err = self._require_connection()
        if err:
            return [err]
        try:
            repo   = self._get_repo(repo_name)
            kwargs = {"ref": branch} if branch else {}
            contents = repo.get_contents(path or "/", **kwargs)
            return [f"{'📁' if c.type == 'dir' else '📄'}  {c.path}" for c in contents]
        except Exception as e:
            return [f"Error: {e}"]

    def get_readme(self, repo_name: str) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._get_repo(repo_name)
            readme = repo.get_readme()
            return base64.b64decode(readme.content).decode("utf-8", errors="replace")
        except Exception as e:
            return f"No README found: {e}"

    # ── Issue Operations ──────────────────────────────────────────────────────
    def list_issues(self, repo_name: str, state: str = "open",
                    limit: int = 20) -> List[Dict[str, Any]]:
        err = self._require_connection()
        if err:
            return [{"number": 0, "title": err, "state": "error", "url": ""}]
        try:
            repo   = self._get_repo(repo_name)
            issues = list(repo.get_issues(state=state))[:limit]
            return [{
                "number" : i.number,
                "title"  : i.title,
                "state"  : i.state,
                "labels" : [l.name for l in i.labels],
                "user"   : i.user.login,
                "url"    : i.html_url,
                "body"   : (i.body or "")[:200],
            } for i in issues]
        except Exception as e:
            return [{"number": 0, "title": f"Error: {e}", "state": "error", "url": ""}]

    def create_issue(self, repo_name: str, title: str,
                     body: str = "", labels: List[str] = None) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo  = self._get_repo(repo_name)
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
            )
            return f"✅ Issue #{issue.number} created → {issue.html_url}"
        except Exception as e:
            return f"Error: {e}"

    def close_issue(self, repo_name: str, issue_number: int) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo  = self._get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            issue.edit(state="closed")
            return f"✅ Issue #{issue_number} closed."
        except Exception as e:
            return f"Error: {e}"

    def add_issue_comment(self, repo_name: str, issue_number: int,
                          comment: str) -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo  = self._get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            issue.create_comment(comment)
            return f"✅ Comment added to issue #{issue_number}"
        except Exception as e:
            return f"Error: {e}"

    # ── Pull Request Operations ───────────────────────────────────────────────
    def list_pull_requests(self, repo_name: str, state: str = "open",
                           limit: int = 20) -> List[Dict[str, Any]]:
        err = self._require_connection()
        if err:
            return [{"number": 0, "title": err, "state": "error"}]
        try:
            repo = self._get_repo(repo_name)
            prs  = list(repo.get_pulls(state=state))[:limit]
            return [{
                "number"  : p.number,
                "title"   : p.title,
                "state"   : p.state,
                "user"    : p.user.login,
                "head"    : p.head.ref,
                "base"    : p.base.ref,
                "url"     : p.html_url,
                "mergeable": p.mergeable,
            } for p in prs]
        except Exception as e:
            return [{"number": 0, "title": f"Error: {e}", "state": "error"}]

    def create_pull_request(self, repo_name: str, title: str, body: str,
                            head: str, base: str = "") -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            repo = self._get_repo(repo_name)
            pr   = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base or repo.default_branch,
            )
            return f"✅ PR #{pr.number} created → {pr.html_url}"
        except Exception as e:
            return f"Error: {e}"

    def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """Return the unified diff of a PR for AI review."""
        err = self._require_connection()
        if err:
            return err
        try:
            repo  = self._get_repo(repo_name)
            pr    = repo.get_pull(pr_number)
            files = pr.get_files()
            lines = [f"PR #{pr_number}: {pr.title}\n"]
            for f in files:
                lines.append(f"\n--- {f.filename} (+{f.additions} -{f.deletions}) ---")
                if f.patch:
                    lines.append(f.patch[:1000])   # cap per file
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    # ── AI-Assisted Code Review ───────────────────────────────────────────────
    def ai_review_pr(self, repo_name: str, pr_number: int,
                     ai_brain) -> str:
        """Get AI-powered review of a pull request diff."""
        diff = self.get_pr_diff(repo_name, pr_number)
        if diff.startswith("Error"):
            return diff
        prompt = (
            f"You are a senior software engineer. Review this pull request diff "
            f"and provide constructive feedback on code quality, potential bugs, "
            f"performance, and best practices.\n\n{diff}"
        )
        return ai_brain.chat(prompt)

    # ── User/Org Info ─────────────────────────────────────────────────────────
    def get_user_info(self, username: str = "") -> str:
        err = self._require_connection()
        if err:
            return err
        try:
            user = self._gh.get_user(username) if username else self._user
            return (
                f"👤 {user.name or user.login} (@{user.login})\n"
                f"   Bio      : {user.bio or 'N/A'}\n"
                f"   Repos    : {user.public_repos} public\n"
                f"   Followers: {user.followers}\n"
                f"   Following: {user.following}\n"
                f"   URL      : {user.html_url}"
            )
        except Exception as e:
            return f"Error: {e}"

    def list_notifications(self, limit: int = 10) -> List[Dict[str, str]]:
        err = self._require_connection()
        if err:
            return [{"subject": err, "reason": "error", "repo": ""}]
        try:
            notes = list(self._user.get_notifications())[:limit]
            return [{
                "subject": n.subject.title,
                "reason" : n.reason,
                "repo"   : n.repository.full_name,
                "unread" : str(n.unread),
            } for n in notes]
        except Exception as e:
            return [{"subject": f"Error: {e}", "reason": "error", "repo": ""}]
