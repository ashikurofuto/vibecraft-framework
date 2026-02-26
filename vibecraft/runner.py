"""
Legacy re-export for backward compatibility.

This module re-exports SimpleRunner as SkillRunner for v0.3 compatibility.
New code should import from vibecraft.modes.simple instead.
"""

from .modes.simple.runner import SimpleRunner

# Legacy alias for backward compatibility
SkillRunner = SimpleRunner

__all__ = ["SkillRunner", "SimpleRunner"]
