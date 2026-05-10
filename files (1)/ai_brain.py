"""
jarvis/ai_brain.py — AI chat & code generation for J.A.R.V.I.S.
Supports OpenAI GPT-4o with conversation memory.
"""

from __future__ import annotations
from typing import List, Dict

import config

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


SYSTEM_PROMPT = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), 
an advanced AI assistant integrated with GitHub. You are helpful, precise, and concise.
When asked about GitHub, provide actionable and accurate information.
When generating code, write clean, production-quality Python with docstrings.
Keep responses under 300 words unless asked for detail."""


class AIBrain:
    """Wraps OpenAI API with conversation history and specialised prompts."""

    def __init__(self):
        self._client = None
        self._history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._init()

    def _init(self):
        if not OPENAI_AVAILABLE:
            print("[AI Brain] openai package not installed. Run: pip install openai")
            return
        if not config.OPENAI_API_KEY:
            print("[AI Brain] No OPENAI_API_KEY set in .env")
            return
        self._client = OpenAI(api_key=config.OPENAI_API_KEY)
        print(f"[AI Brain] OpenAI connected (model: {config.OPENAI_MODEL})")

    def chat(self, message: str) -> str:
        """Send a message and get a response, maintaining history."""
        if not self._client:
            return "[AI Brain] OpenAI not configured. Add OPENAI_API_KEY to .env"
        try:
            self._history.append({"role": "user", "content": message})
            response = self._client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=self._history,
                max_tokens=1000,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            self._history.append({"role": "assistant", "content": reply})
            # Keep history manageable (last 20 exchanges + system)
            if len(self._history) > 41:
                self._history = [self._history[0]] + self._history[-40:]
            return reply
        except Exception as e:
            return f"[AI Brain] Error: {e}"

    def generate_code(self, description: str, language: str = "Python") -> str:
        """Generate code for a given description."""
        prompt = (
            f"Write clean, production-quality {language} code for: {description}\n"
            f"Include docstrings and type hints. Return only the code, no explanations."
        )
        return self.chat(prompt)

    def review_code(self, code: str) -> str:
        """Review code and suggest improvements."""
        prompt = (
            f"Review this code and suggest improvements for readability, "
            f"performance, and best practices:\n\n```\n{code}\n```"
        )
        return self.chat(prompt)

    def explain_code(self, code: str) -> str:
        """Explain what a piece of code does."""
        return self.chat(f"Explain this code clearly and concisely:\n\n```\n{code}\n```")

    def summarise_pr(self, diff: str) -> str:
        """Summarise a PR diff."""
        return self.chat(
            f"Summarise this pull request diff in 3–5 bullet points, "
            f"highlighting the main changes:\n\n{diff[:3000]}"
        )

    def clear_history(self):
        """Reset conversation history."""
        self._history = [{"role": "system", "content": SYSTEM_PROMPT}]
