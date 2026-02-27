"""
Tests for Vibecraft BootstrapperFactory.

Tests verify factory creates correct bootstrapper instances based on mode.
"""

import pytest
from pathlib import Path

from vibecraft.core.factory import BootstrapperFactory
from vibecraft.core.config import VibecraftConfig, ProjectMode


class TestBootstrapperFactory:
    """Tests for BootstrapperFactory.create() method."""

    # ------------------------------------------------------------------
    #  Simple mode tests (parameterized)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("mode_input,description", [
        (ProjectMode.SIMPLE, "ProjectMode.SIMPLE enum"),
        ("simple", "lowercase string 'simple'"),
        ("SIMPLE", "uppercase string 'SIMPLE'"),
        ("Simple", "titlecase string 'Simple'"),
    ])
    def test_creates_simple_bootstrapper_for_all_simple_mode_variants(
        self, mode_input, description, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory returns SimpleBootstrapper for all SIMPLE mode variants: {description}."""
        # Act
        result = BootstrapperFactory.create(
            mode=mode_input,
            project_root=factory_project_root,
            config=factory_config,
        )

        # Assert
        assert type(result).__name__ == "SimpleBootstrapper"
        assert result.project_root == factory_project_root
        assert result.config == factory_config

    # ------------------------------------------------------------------
    #  Modular mode tests (parameterized)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("mode_input,description", [
        (ProjectMode.MODULAR, "ProjectMode.MODULAR enum"),
        ("modular", "lowercase string 'modular'"),
        ("MODULAR", "uppercase string 'MODULAR'"),
        ("Modular", "titlecase string 'Modular'"),
    ])
    def test_creates_modular_bootstrapper_for_all_modular_mode_variants(
        self, mode_input, description, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory returns ModularBootstrapper for all MODULAR mode variants: {description}."""
        # Act
        result = BootstrapperFactory.create(
            mode=mode_input,
            project_root=factory_project_root,
            config=factory_config,
        )

        # Assert
        assert type(result).__name__ == "ModularBootstrapper"
        assert result.project_root == factory_project_root
        assert result.config == factory_config

    # ------------------------------------------------------------------
    #  Error handling tests
    # ------------------------------------------------------------------

    def test_raises_value_error_for_unknown_mode_string(
        self, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory raises ValueError with message for unknown mode."""
        # Act & Assert
        with pytest.raises(ValueError, match="Unknown mode: 'invalid_mode'"):
            BootstrapperFactory.create(
                mode="invalid_mode",
                project_root=factory_project_root,
                config=factory_config,
            )

    # ------------------------------------------------------------------
    #  Kwargs passing tests (parameterized)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("kwarg_name,kwarg_value,expected_value", [
        ("research_path", lambda tmp: tmp / "custom_research.md", "custom_research.md"),
        ("stack_path", lambda tmp: tmp / "custom_stack.md", "custom_stack.md"),
        ("custom_agents_path", lambda tmp: tmp / "agents.yaml", "agents.yaml"),
    ])
    def test_passes_custom_paths_to_simple_bootstrapper(
        self, kwarg_name, kwarg_value, expected_value,
        factory_config: VibecraftConfig, factory_project_root: Path, tmp_path: Path
    ):
        """Factory passes {kwarg_name} kwarg to SimpleBootstrapper."""
        # Arrange
        custom_path = kwarg_value(tmp_path)
        if kwarg_name == "custom_agents_path":
            custom_path.write_text("- name: custom")
        else:
            custom_path.write_text(f"# Custom {kwarg_name}")

        # Act
        result = BootstrapperFactory.create(
            mode=ProjectMode.SIMPLE,
            project_root=factory_project_root,
            config=factory_config,
            **{kwarg_name: custom_path}
        )

        # Assert
        assert getattr(result, kwarg_name) == custom_path

    def test_passes_force_flag_to_simple_bootstrapper(
        self, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory passes force=True kwarg to SimpleBootstrapper."""
        # Act
        result = BootstrapperFactory.create(
            mode=ProjectMode.SIMPLE,
            project_root=factory_project_root,
            config=factory_config,
            force=True,
        )

        # Assert
        assert result.force is True

    def test_force_false_by_default(
        self, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory passes force=False by default."""
        # Act
        result = BootstrapperFactory.create(
            mode=ProjectMode.SIMPLE,
            project_root=factory_project_root,
            config=factory_config,
        )

        # Assert
        assert result.force is False

    # ------------------------------------------------------------------
    #  Default paths tests
    # ------------------------------------------------------------------

    def test_uses_default_research_path_when_not_provided(
        self, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory uses project_root/docs/research.md when research_path not provided."""
        # Act
        result = BootstrapperFactory.create(
            mode=ProjectMode.SIMPLE,
            project_root=factory_project_root,
            config=factory_config,
        )

        # Assert
        expected = factory_project_root / "docs" / "research.md"
        assert result.research_path == expected

    def test_uses_default_stack_path_when_not_provided(
        self, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory uses project_root/docs/stack.md when stack_path not provided."""
        # Act
        result = BootstrapperFactory.create(
            mode=ProjectMode.SIMPLE,
            project_root=factory_project_root,
            config=factory_config,
        )

        # Assert
        expected = factory_project_root / "docs" / "stack.md"
        assert result.stack_path == expected

    def test_custom_agents_path_none_when_not_provided(
        self, factory_config: VibecraftConfig, factory_project_root: Path
    ):
        """Factory passes custom_agents_path=None when not provided."""
        # Act
        result = BootstrapperFactory.create(
            mode=ProjectMode.SIMPLE,
            project_root=factory_project_root,
            config=factory_config,
        )

        # Assert
        assert result.custom_agents_path is None
