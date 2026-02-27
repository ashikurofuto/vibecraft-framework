"""
Tests for DependencyAnalyzer module.

Tests verify that DependencyAnalyzer properly analyzes module dependencies,
detects cycles, and computes correct build order.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from vibecraft.modes.modular.dependency_analyzer import DependencyAnalyzer
from vibecraft.core.exceptions import CyclicDependencyError, MissingDependencyError


class TestDependencyAnalyzerInit:
    """Tests for DependencyAnalyzer initialization."""

    def test_init_creates_analyzer(self, tmp_path: Path):
        """DependencyAnalyzer can be instantiated."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = []

        # Act
        analyzer = DependencyAnalyzer(mock_registry)

        # Assert
        assert analyzer is not None
        assert analyzer.registry == mock_registry

    def test_init_builds_graph(self, tmp_path: Path):
        """DependencyAnalyzer builds graph on initialization."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = []

        # Act
        analyzer = DependencyAnalyzer(mock_registry)

        # Assert
        assert analyzer.graph is not None
        assert analyzer.graph.number_of_nodes() == 0

    def test_init_with_modules(self, tmp_path: Path):
        """DependencyAnalyzer builds graph with modules."""
        # Arrange
        mock_module1 = MagicMock()
        mock_module1.name = "auth"
        mock_module1.dependencies = []

        mock_module2 = MagicMock()
        mock_module2.name = "api"
        mock_module2.dependencies = ["auth"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_module1, mock_module2]

        # Act
        analyzer = DependencyAnalyzer(mock_registry)

        # Assert
        assert analyzer.graph.number_of_nodes() == 2
        assert analyzer.graph.number_of_edges() == 1


class TestBuildGraph:
    """Tests for _build_graph method."""

    def test_build_graph_empty_registry(self):
        """_build_graph creates empty graph for empty registry."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = []

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        graph = analyzer._build_graph()

        # Assert
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_build_graph_single_module(self):
        """_build_graph handles single module without dependencies."""
        # Arrange
        mock_module = MagicMock()
        mock_module.name = "auth"
        mock_module.dependencies = []

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_module]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        graph = analyzer._build_graph()

        # Assert
        assert graph.number_of_nodes() == 1
        assert "auth" in graph.nodes

    def test_build_graph_with_dependencies(self):
        """_build_graph creates edges for dependencies."""
        # Arrange
        mock_db = MagicMock()
        mock_db.name = "database"
        mock_db.dependencies = []

        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["database"]

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["auth", "database"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_db, mock_auth, mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        graph = analyzer._build_graph()

        # Assert
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 3
        # Edge direction: dependency -> dependent
        assert graph.has_edge("database", "auth")
        assert graph.has_edge("database", "api")
        assert graph.has_edge("auth", "api")

    def test_build_graph_edge_direction(self):
        """_build_graph creates edges from dependency to dependent."""
        # Arrange
        mock_dep = MagicMock()
        mock_dep.name = "dependency"
        mock_dep.dependencies = []

        mock_dependent = MagicMock()
        mock_dependent.name = "dependent"
        mock_dependent.dependencies = ["dependency"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_dep, mock_dependent]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        graph = analyzer._build_graph()

        # Assert - edge goes FROM dependency TO dependent
        assert graph.has_edge("dependency", "dependent")
        assert not graph.has_edge("dependent", "dependency")


class TestValidateDependencies:
    """Tests for validate_dependencies method."""

    def test_validate_empty_registry(self):
        """validate_dependencies passes for empty registry."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = []

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert - should not raise
        analyzer.validate_dependencies()

    def test_validate_valid_dependencies(self):
        """validate_dependencies passes when all dependencies exist."""
        # Arrange
        mock_db = MagicMock()
        mock_db.name = "database"
        mock_db.dependencies = []

        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["database"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_db, mock_auth]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert - should not raise
        analyzer.validate_dependencies()

    def test_validate_missing_dependency(self):
        """validate_dependencies raises MissingDependencyError for missing dep."""
        # Arrange
        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["nonexistent"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_auth]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(MissingDependencyError, match="nonexistent"):
            analyzer.validate_dependencies()

    def test_validate_multiple_missing_dependencies(self):
        """validate_dependencies detects multiple missing dependencies."""
        # Arrange
        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["auth", "database", "cache"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(MissingDependencyError):
            analyzer.validate_dependencies()

    def test_validate_circular_dependency(self):
        """validate_dependencies raises CyclicDependencyError for cycles."""
        # Arrange
        mock_a = MagicMock()
        mock_a.name = "a"
        mock_a.dependencies = ["b"]

        mock_b = MagicMock()
        mock_b.name = "b"
        mock_b.dependencies = ["a"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_a, mock_b]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(CyclicDependencyError, match="Circular"):
            analyzer.validate_dependencies()

    def test_validate_error_message_includes_module(self):
        """validate_dependencies error includes module name."""
        # Arrange
        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["missing"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_auth]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(MissingDependencyError) as exc_info:
            analyzer.validate_dependencies()

        assert "auth" in str(exc_info.value)
        assert "missing" in str(exc_info.value)


class TestHasCycle:
    """Tests for has_cycle method."""

    def test_has_cycle_empty_graph(self):
        """has_cycle returns False for empty graph."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = []

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        result = analyzer.has_cycle()

        # Assert
        assert result is False

    def test_has_cycle_no_dependencies(self):
        """has_cycle returns False for modules without dependencies."""
        # Arrange
        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = []

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = []

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_auth, mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        result = analyzer.has_cycle()

        # Assert
        assert result is False

    def test_has_cycle_simple_cycle(self):
        """has_cycle detects simple A -> B -> A cycle."""
        # Arrange
        mock_a = MagicMock()
        mock_a.name = "a"
        mock_a.dependencies = ["b"]

        mock_b = MagicMock()
        mock_b.name = "b"
        mock_b.dependencies = ["a"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_a, mock_b]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        result = analyzer.has_cycle()

        # Assert
        assert result is True

    def test_has_cycle_complex_cycle(self):
        """has_cycle detects complex A -> B -> C -> A cycle."""
        # Arrange
        mock_a = MagicMock()
        mock_a.name = "a"
        mock_a.dependencies = ["c"]

        mock_b = MagicMock()
        mock_b.name = "b"
        mock_b.dependencies = ["a"]

        mock_c = MagicMock()
        mock_c.name = "c"
        mock_c.dependencies = ["b"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_a, mock_b, mock_c]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        result = analyzer.has_cycle()

        # Assert
        assert result is True

    def test_has_cycle_self_dependency(self):
        """has_cycle detects self-dependency."""
        # Arrange
        mock_self = MagicMock()
        mock_self.name = "self"
        mock_self.dependencies = ["self"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_self]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        result = analyzer.has_cycle()

        # Assert
        assert result is True

    def test_has_cycle_no_cycle_linear_chain(self):
        """has_cycle returns False for linear dependency chain."""
        # Arrange
        mock_db = MagicMock()
        mock_db.name = "database"
        mock_db.dependencies = []

        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["database"]

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["auth"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_db, mock_auth, mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        result = analyzer.has_cycle()

        # Assert
        assert result is False


class TestGetBuildOrder:
    """Tests for get_build_order method."""

    def test_get_build_order_empty(self):
        """get_build_order returns empty list for empty registry."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = []

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        order = analyzer.get_build_order()

        # Assert
        assert order == []

    def test_get_build_order_single_module(self):
        """get_build_order returns single module."""
        # Arrange
        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = []

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_auth]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        order = analyzer.get_build_order()

        # Assert
        assert order == ["auth"]

    def test_get_build_order_no_dependencies(self):
        """get_build_order handles modules without dependencies."""
        # Arrange
        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = []

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = []

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_auth, mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        order = analyzer.get_build_order()

        # Assert
        assert len(order) == 2
        assert set(order) == {"auth", "api"}

    def test_get_build_order_respects_dependencies(self):
        """get_build_order returns dependencies before dependents."""
        # Arrange
        mock_db = MagicMock()
        mock_db.name = "database"
        mock_db.dependencies = []

        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["database"]

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["auth", "database"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_db, mock_auth, mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        order = analyzer.get_build_order()

        # Assert
        assert order.index("database") < order.index("auth")
        assert order.index("database") < order.index("api")
        assert order.index("auth") < order.index("api")

    def test_get_build_order_complex_dependencies(self):
        """get_build_order handles complex dependency graphs."""
        # Arrange
        mock_core = MagicMock()
        mock_core.name = "core"
        mock_core.dependencies = []

        mock_db = MagicMock()
        mock_db.name = "database"
        mock_db.dependencies = ["core"]

        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["core", "database"]

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["auth"]

        mock_cache = MagicMock()
        mock_cache.name = "cache"
        mock_cache.dependencies = ["core"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [
            mock_core, mock_db, mock_auth, mock_api, mock_cache
        ]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act
        order = analyzer.get_build_order()

        # Assert
        assert order[0] == "core"  # core must be first
        assert order.index("database") < order.index("auth")
        assert order.index("auth") < order.index("api")

    def test_get_build_order_raises_on_cycle(self):
        """get_build_order raises CyclicDependencyError for cycles."""
        # Arrange
        mock_a = MagicMock()
        mock_a.name = "a"
        mock_a.dependencies = ["b"]

        mock_b = MagicMock()
        mock_b.name = "b"
        mock_b.dependencies = ["a"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_a, mock_b]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(CyclicDependencyError, match="circular"):
            analyzer.get_build_order()


class TestDependencyAnalyzerIntegration:
    """Integration tests for DependencyAnalyzer."""

    def test_full_workflow_valid_project(self):
        """Complete workflow: build graph -> validate -> get order."""
        # Arrange
        mock_db = MagicMock()
        mock_db.name = "database"
        mock_db.dependencies = []

        mock_auth = MagicMock()
        mock_auth.name = "auth"
        mock_auth.dependencies = ["database"]

        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["auth", "database"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_db, mock_auth, mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        # 1. Validate should pass
        analyzer.validate_dependencies()

        # 2. No cycles
        assert analyzer.has_cycle() is False

        # 3. Get valid build order
        order = analyzer.get_build_order()
        assert len(order) == 3
        assert order.index("database") < order.index("auth")
        assert order.index("auth") < order.index("api")

    def test_full_workflow_missing_dependency(self):
        """Complete workflow fails on missing dependency."""
        # Arrange
        mock_api = MagicMock()
        mock_api.name = "api"
        mock_api.dependencies = ["missing"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_api]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(MissingDependencyError):
            analyzer.validate_dependencies()

        # Build order still returns nodes (including missing dep as node)
        order = analyzer.get_build_order()
        assert len(order) == 2
        assert "api" in order
        assert "missing" in order

    def test_full_workflow_circular_dependency(self):
        """Complete workflow fails on circular dependency."""
        # Arrange
        mock_a = MagicMock()
        mock_a.name = "a"
        mock_a.dependencies = ["b"]

        mock_b = MagicMock()
        mock_b.name = "b"
        mock_b.dependencies = ["a"]

        mock_registry = MagicMock()
        mock_registry.get_all_modules.return_value = [mock_a, mock_b]

        analyzer = DependencyAnalyzer(mock_registry)

        # Act & Assert
        with pytest.raises(CyclicDependencyError):
            analyzer.validate_dependencies()

        assert analyzer.has_cycle() is True

        with pytest.raises(CyclicDependencyError):
            analyzer.get_build_order()
