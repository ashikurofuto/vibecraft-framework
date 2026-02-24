"""
AdapterFactory — resolves the correct LLM adapter at runtime.

Set VIBECRAFT_BACKEND env var to switch backends:
  qwen     (default) — Qwen CLI via subprocess
  clipboard          — dry-run: just copies prompt, no LLM call
  echo               — test stub: returns prompt back as response

Adding a new backend:
  1. Create vibecraft/adapters/my_adapter.py implementing BaseAdapter
  2. Register it in _REGISTRY below
"""

import os
from .base_adapter import BaseAdapter
from .qwen_adapter import QwenAdapter
from .clipboard_adapter import ClipboardAdapter
from .echo_adapter import EchoAdapter

_REGISTRY: dict[str, type[BaseAdapter]] = {
    "qwen":      QwenAdapter,
    "clipboard": ClipboardAdapter,
    "echo":      EchoAdapter,
}


def get_adapter(stream: bool = True) -> BaseAdapter:
    backend = os.environ.get("VIBECRAFT_BACKEND", "qwen").lower()
    cls = _REGISTRY.get(backend)
    if cls is None:
        available = ", ".join(_REGISTRY.keys())
        raise ValueError(
            f"Unknown VIBECRAFT_BACKEND='{backend}'. "
            f"Available: {available}"
        )
    # ClipboardAdapter and EchoAdapter don't use stream
    if backend in ("clipboard", "echo"):
        return cls()
    return cls(stream=stream)
