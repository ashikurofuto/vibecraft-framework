"""
Legacy re-export for backward compatibility.

This module re-exports SimpleBootstrapper as Bootstrapper for v0.3 compatibility.
New code should import from vibecraft.modes.simple instead.
"""

from .modes.simple.bootstrapper import SimpleBootstrapper

# Legacy alias for backward compatibility
Bootstrapper = SimpleBootstrapper

__all__ = ["Bootstrapper", "SimpleBootstrapper"]
