"""Base adapter interface. All adapters must implement call()."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseAdapter(ABC):
    @abstractmethod
    def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
        """Send prompt, return response text."""
        ...
