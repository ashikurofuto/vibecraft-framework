"""
Vibecraft entry point with Windows UTF-8 encoding fix.

This module ensures proper UTF-8 encoding on Windows before
importing and running the CLI.
"""

import os
import sys


def _setup_windows_encoding():
    """Configure UTF-8 encoding for Windows consoles."""
    if sys.platform == "win32":
        # Set environment variable for subprocess compatibility
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        # Reconfigure stdout/stderr for Unicode output
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, UnicodeError):
            pass
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, UnicodeError):
            pass


# Apply fixes before importing CLI
_setup_windows_encoding()

from vibecraft.cli import main

if __name__ == "__main__":
    main()
