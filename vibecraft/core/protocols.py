"""
Protocols for structural subtyping in Vibecraft Framework.

Protocols define interfaces that classes can implement without explicit inheritance.
This enables flexible, duck-typed polymorphism with static type checking support.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Creatable(Protocol):
    """Protocol for objects that can be created."""

    def create(self) -> None:
        """Create the resource."""
        ...


@runtime_checkable
class Listable(Protocol):
    """Protocol for objects that can list items."""

    def list(self) -> list[dict]:
        """List items as dictionaries.

        Returns:
            List of dictionaries representing the items.
        """
        ...


@runtime_checkable
class Buildable(Protocol):
    """Protocol for objects that can be built."""

    def build(self) -> None:
        """Build the resource."""
        ...
