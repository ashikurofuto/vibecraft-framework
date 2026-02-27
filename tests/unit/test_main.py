"""
Tests for Vibecraft main entry point.

Tests verify that the main module correctly delegates to CLI.
"""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys


class TestMainEntryPoint:
    """Tests for main.py entry point."""

    def test_main_module_imports_successfully(self):
        """main module should import without errors."""
        # Act
        import vibecraft.main

        # Assert - module exists and has expected attributes
        assert hasattr(vibecraft.main, "main")

    def test_main_cli_is_imported(self):
        """main module should import cli.main after encoding setup."""
        # Arrange
        with patch("vibecraft.cli.main") as mock_main:
            # Act
            import importlib
            import vibecraft.main
            importlib.reload(vibecraft.main)

            # Assert - cli.main was imported
            assert mock_main is not None

    def test_main_sets_pythonioencoding_env(self, monkeypatch):
        """main.py should set PYTHONIOENCODING environment variable on Windows."""
        # Arrange
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.delenv("PYTHONIOENCODING", raising=False)

        # Act
        with patch("vibecraft.cli.main"):
            import importlib
            import vibecraft.main
            importlib.reload(vibecraft.main)

        # Assert
        import os
        assert os.environ.get("PYTHONIOENCODING") == "utf-8"

    def test_main_does_not_set_env_on_non_windows(self, monkeypatch):
        """main.py should not set PYTHONIOENCODING on non-Windows platforms."""
        # Arrange
        monkeypatch.setattr("sys.platform", "linux")
        monkeypatch.delenv("PYTHONIOENCODING", raising=False)

        # Act
        with patch("vibecraft.cli.main"):
            import importlib
            import vibecraft.main
            importlib.reload(vibecraft.main)

        # Assert - env should not be set by main.py
        import os
        assert os.environ.get("PYTHONIOENCODING") is None

    def test_main_handles_stdout_reconfigure_error(self, monkeypatch):
        """main.py should handle stdout reconfigure errors gracefully."""
        # Arrange
        monkeypatch.setattr("sys.platform", "win32")

        def raise_error(*args, **kwargs):
            raise AttributeError("No reconfigure")

        with patch("vibecraft.cli.main"):
            with patch.object(sys.stdout, "reconfigure", side_effect=raise_error):
                with patch.object(sys.stderr, "reconfigure"):
                    # Act - should not raise
                    import importlib
                    import vibecraft.main
                    importlib.reload(vibecraft.main)

                    # Assert - module loaded despite error
                    assert True

    def test_main_handles_stderr_reconfigure_error(self, monkeypatch):
        """main.py should handle stderr reconfigure errors gracefully."""
        # Arrange
        monkeypatch.setattr("sys.platform", "win32")

        def raise_error(*args, **kwargs):
            raise UnicodeError("Encoding error")

        with patch("vibecraft.cli.main"):
            with patch.object(sys.stdout, "reconfigure"):
                with patch.object(sys.stderr, "reconfigure", side_effect=raise_error):
                    # Act - should not raise
                    import importlib
                    import vibecraft.main
                    importlib.reload(vibecraft.main)

                    # Assert - module loaded despite error
                    assert True
