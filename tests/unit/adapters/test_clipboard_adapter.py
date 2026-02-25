"""Tests for ClipboardAdapter."""

import pytest
from pathlib import Path
from vibecraft.adapters.clipboard_adapter import ClipboardAdapter


class TestClipboardAdapter:
    """Tests for ClipboardAdapter.call()."""

    def test_returns_placeholder(self, tmp_path):
        """Should return placeholder response."""
        adapter = ClipboardAdapter()
        response = adapter.call("Test prompt")
        assert "DRY-RUN" in response
        assert "no LLM response" in response

    def test_ignores_context_files(self, tmp_path):
        """Should ignore context_files parameter."""
        adapter = ClipboardAdapter()
        ctx_file = tmp_path / "context.md"
        ctx_file.write_text("Context")
        response = adapter.call("Test prompt", context_files=[ctx_file])
        assert "DRY-RUN" in response


class TestBanner:
    """Tests for banner formatting."""

    def test_banner_uses_ascii(self):
        """Banner should use ASCII characters only (no Unicode)."""
        from vibecraft.adapters.clipboard_adapter import _BANNER
        # Should not contain Unicode box-drawing characters
        assert "─" not in _BANNER
        assert "-" in _BANNER
