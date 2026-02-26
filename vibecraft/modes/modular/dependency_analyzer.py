"""
Dependency Analyzer for Vibecraft Framework.

Analyzes module dependencies, detects cycles, and computes build order.
"""
from typing import List
import networkx as nx

from vibecraft.modes.modular.module_registry import ModuleRegistry
from vibecraft.core.exceptions import CyclicDependencyError


class DependencyAnalyzer:
    """
    Analyzes dependencies between modules.

    Uses networkx for graph operations:
    - Cycle detection using DFS
    - Topological sort for build order

    Attributes:
        registry: ModuleRegistry instance containing module information
        graph: Directed graph of module dependencies
    """

    def __init__(self, registry: ModuleRegistry):
        """
        Initialize DependencyAnalyzer.

        Args:
            registry: ModuleRegistry instance with module information
        """
        self.registry = registry
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        """
        Build dependency graph from registry.

        Creates a directed graph where:
        - Nodes are module names
        - Edges point from dependency to dependent module
          (e.g., database -> auth means auth depends on database)

        This direction ensures topological sort returns dependencies first.

        Returns:
            networkx DiGraph with module dependencies
        """
        graph = nx.DiGraph()
        modules = self.registry.get_all_modules()

        # Add all modules as nodes
        for module in modules:
            graph.add_node(module.name)

        # Add edges for dependencies
        # Edge goes FROM dependency TO dependent module
        # e.g., if auth depends on database, edge is: database -> auth
        for module in modules:
            for dep in module.dependencies:
                graph.add_edge(dep, module.name)

        return graph

    def validate_dependencies(self) -> None:
        """
        Validate all dependencies exist.

        Checks:
        1. All dependencies reference existing modules
        2. No circular dependencies exist

        Raises:
            MissingDependencyError: If a dependency doesn't exist
            CyclicDependencyError: If circular dependencies detected
        """
        from vibecraft.core.exceptions import MissingDependencyError
        
        modules = self.registry.get_all_modules()

        # Check existence of all dependencies
        module_names = {m.name for m in modules}
        for module in modules:
            for dep in module.dependencies:
                if dep not in module_names:
                    raise MissingDependencyError(
                        f"Module '{module.name}' depends on non-existent module '{dep}'"
                    )

        # Check for cycles
        if self.has_cycle():
            raise CyclicDependencyError("Circular dependencies detected")

    def has_cycle(self) -> bool:
        """
        Check if dependency graph has cycles.

        Uses networkx.find_cycle() which implements DFS-based cycle detection.

        Returns:
            True if cycle exists, False otherwise
        """
        try:
            nx.find_cycle(self.graph)
            return True
        except nx.NetworkXNoCycle:
            return False

    def get_build_order(self) -> List[str]:
        """
        Get topological build order for modules.

        Returns modules in order such that all dependencies come before
        the modules that depend on them.

        Returns:
            List of module names in build order

        Raises:
            CyclicDependencyError: If graph has cycles (topological sort impossible)
        """
        if self.has_cycle():
            raise CyclicDependencyError(
                "Cannot determine build order: circular dependencies detected"
            )

        # Topological sort returns dependencies before dependents
        return list(nx.topological_sort(self.graph))
