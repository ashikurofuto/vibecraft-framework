"""
Simple mode for Vibecraft Framework.

This module contains the legacy v0.3 bootstrapper and runner
for simple mode projects (non-modular workflow).
"""

from .bootstrapper import SimpleBootstrapper
from .runner import SimpleRunner

__all__ = ["SimpleBootstrapper", "SimpleRunner"]
