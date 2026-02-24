"""
EchoAdapter — test/debug stub.

Returns the prompt as the response. Useful for unit tests and CI.
"""

from pathlib import Path
from .base_adapter import BaseAdapter


class EchoAdapter(BaseAdapter):
    def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
        print("\n  [ECHO ADAPTER] Returning prompt as response.\n")
        return f"<!-- ECHO RESPONSE -->\n{prompt}"
