"""
Tests for structural subtyping protocols.

These tests verify that:
1. Protocols are defined correctly
2. Classes can implement protocols
3. runtime_checkable protocols work with isinstance
"""

import pytest
from typing import runtime_checkable

from vibecraft.core.protocols import Creatable, Listable, Buildable


class TestCreatableProtocol:
    """Tests for Creatable protocol."""

    def test_creatable_protocol_is_runtime_checkable(self):
        """Creatable protocol is runtime_checkable."""
        # Assert
        assert hasattr(Creatable, "__protocol_attrs__")

    def test_class_implements_creatable(self):
        """Class with create() method implements Creatable."""
        # Arrange
        class MyCreatable:
            def create(self) -> None:
                pass

        # Act
        instance = MyCreatable()

        # Assert
        assert isinstance(instance, Creatable)

    def test_class_without_create_not_creatable(self):
        """Class without create() method does not implement Creatable."""
        # Arrange
        class NotCreatable:
            def other_method(self) -> None:
                pass

        # Act
        instance = NotCreatable()

        # Assert
        assert not isinstance(instance, Creatable)

    def test_creatable_with_return_value(self):
        """Creatable works with methods that return values."""
        # Arrange
        class CreatableWithReturn:
            def create(self) -> str:
                return "created"

        # Act
        instance = CreatableWithReturn()

        # Assert
        assert isinstance(instance, Creatable)
        assert instance.create() == "created"


class TestListableProtocol:
    """Tests for Listable protocol."""

    def test_listable_protocol_is_runtime_checkable(self):
        """Listable protocol is runtime_checkable."""
        # Assert
        assert hasattr(Listable, "__protocol_attrs__")

    def test_class_implements_listable(self):
        """Class with list() method implements Listable."""
        # Arrange
        class MyListable:
            def list(self) -> list[dict]:
                return [{"name": "item1"}]

        # Act
        instance = MyListable()

        # Assert
        assert isinstance(instance, Listable)

    def test_listable_returns_list_of_dicts(self):
        """Listable list() method returns list of dicts."""
        # Arrange
        class MyListable:
            def list(self) -> list[dict]:
                return [
                    {"name": "item1", "value": 1},
                    {"name": "item2", "value": 2},
                ]

        # Act
        instance = MyListable()
        result = instance.list()

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_class_without_list_not_listable(self):
        """Class without list() method does not implement Listable."""
        # Arrange
        class NotListable:
            def get_items(self) -> list:
                return []

        # Act
        instance = NotListable()

        # Assert
        assert not isinstance(instance, Listable)


class TestBuildableProtocol:
    """Tests for Buildable protocol."""

    def test_buildable_protocol_is_runtime_checkable(self):
        """Buildable protocol is runtime_checkable."""
        # Assert
        assert hasattr(Buildable, "__protocol_attrs__")

    def test_class_implements_buildable(self):
        """Class with build() method implements Buildable."""
        # Arrange
        class MyBuildable:
            def build(self) -> None:
                pass

        # Act
        instance = MyBuildable()

        # Assert
        assert isinstance(instance, Buildable)

    def test_class_without_build_not_buildable(self):
        """Class without build() method does not implement Buildable."""
        # Arrange
        class NotBuildable:
            def create(self) -> None:
                pass

        # Act
        instance = NotBuildable()

        # Assert
        assert not isinstance(instance, Buildable)


class TestMultipleProtocols:
    """Tests for classes implementing multiple protocols."""

    def test_class_implements_multiple_protocols(self):
        """Class can implement multiple protocols."""
        # Arrange
        class MultiProtocol:
            def create(self) -> None:
                pass

            def list(self) -> list[dict]:
                return []

            def build(self) -> None:
                pass

        # Act
        instance = MultiProtocol()

        # Assert
        assert isinstance(instance, Creatable)
        assert isinstance(instance, Listable)
        assert isinstance(instance, Buildable)

    def test_class_implements_some_protocols(self):
        """Class can implement subset of protocols."""
        # Arrange
        class PartialProtocol:
            def create(self) -> None:
                pass

            def build(self) -> None:
                pass

        # Act
        instance = PartialProtocol()

        # Assert
        assert isinstance(instance, Creatable)
        assert not isinstance(instance, Listable)
        assert isinstance(instance, Buildable)


class TestProtocolStructuralSubtyping:
    """Tests for structural subtyping (duck typing) with protocols."""

    def test_structural_subtyping_creatable(self):
        """Any object with create() method is Creatable."""
        # Arrange - duck-typed object
        class DuckCreatable:
            def create(self) -> None:
                """Not explicitly implementing protocol."""
                pass

        # Act
        instance = DuckCreatable()

        # Assert - structural subtyping works
        assert isinstance(instance, Creatable)

    def test_structural_subtyping_listable(self):
        """Any object with list() -> list[dict] is Listable."""
        # Arrange - duck-typed object
        class DuckListable:
            def list(self) -> list[dict]:
                return [{"key": "value"}]

        # Act
        instance = DuckListable()

        # Assert - structural subtyping works
        assert isinstance(instance, Listable)

    def test_structural_subtyping_buildable(self):
        """Any object with build() method is Buildable."""
        # Arrange - duck-typed object
        class DuckBuildable:
            def build(self) -> None:
                """Not explicitly implementing protocol."""
                pass

        # Act
        instance = DuckBuildable()

        # Assert - structural subtyping works
        assert isinstance(instance, Buildable)
