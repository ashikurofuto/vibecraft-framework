"""
ClipboardAdapter - dry-run backend.

Copies the assembled prompt to clipboard instead of calling an LLM.
Useful for users who want to paste the prompt into any chat interface manually.
"""

import pyperclip
from pathlib import Path
from .base_adapter import BaseAdapter

_BANNER = "\n" + "-" * 60 + "\n"


class ClipboardAdapter(BaseAdapter):
    def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
        try:
            pyperclip.copy(prompt)
            print(_BANNER)
            print("  [CLIPBOARD] DRY-RUN: prompt copied to clipboard.")
            print("  Paste it into your preferred LLM chat interface.")
            print(_BANNER)
        except Exception as e:
            print(f"\n  [WARN] Clipboard unavailable ({e}).")
            print("  Prompt has been saved to .vibecraft/last_prompt_*.md\n")

        # Return a placeholder so the runner can continue without crashing
        return (
            "<!-- DRY-RUN: no LLM response. "
            "Paste the prompt from clipboard into your LLM and save the result manually. -->"
        )
