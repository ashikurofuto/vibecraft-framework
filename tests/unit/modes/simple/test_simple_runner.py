"""
Tests for SimpleRunner step execution and human gate functionality.

Tests verify the core execution flow of the SimpleRunner class.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from vibecraft.modes.simple.runner import SimpleRunner


class TestRunStepSuccessPath:
    """Tests for successful step execution."""

    def test_runStep_executesStepAndReturnsTrue_whenAdapterSucceeds(
        self, tmp_project: Path
    ) -> None:
        """_run_step executes step and returns True when adapter call succeeds."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {
            "name": "Research Step",
            "agent": "researcher",
            "output": "docs/output.md",
        }

        with patch.object(runner.adapter, "call", return_value="# Test Response"):
            # Act
            result = runner._run_step(
                step=step,
                step_number=1,
                total_steps=3,
                skill={"name": "Research Skill"},
                phase=None,
            )

            # Assert
            assert result is True
            assert (tmp_project / "docs" / "output.md").exists()

    def test_runStep_savesOutputToFile_whenOutputPathSpecified(
        self, tmp_project: Path
    ) -> None:
        """_run_step saves adapter response to specified output file."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {
            "agent": "researcher",
            "output": "docs/test.md",
        }
        expected_content = "# Generated Content"

        with patch.object(runner.adapter, "call", return_value=expected_content):
            # Act
            runner._run_step(
                step=step,
                step_number=1,
                total_steps=2,
                skill={},
                phase=None,
            )

            # Assert
            output_file = tmp_project / "docs" / "test.md"
            assert output_file.read_text() == expected_content

    def test_runStep_createsParentDirectories_whenOutputPathDoesNotExist(
        self, tmp_project: Path
    ) -> None:
        """_run_step creates parent directories for output file."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {
            "agent": "researcher",
            "output": "deep/nested/path/file.md",
        }

        with patch.object(runner.adapter, "call", return_value="# Content"):
            # Act
            runner._run_step(
                step=step,
                step_number=1,
                total_steps=2,
                skill={},
                phase=None,
            )

            # Assert
            output_file = tmp_project / "deep" / "nested" / "path" / "file.md"
            assert output_file.exists()

    def test_runStep_savesPromptWithTimestamp_whenStepExecutes(
        self, tmp_project: Path
    ) -> None:
        """_run_step saves prompt to versioned file before execution."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher", "name": "Test Step"}

        with patch.object(runner.adapter, "call", return_value="# Response"):
            # Act
            runner._run_step(
                step=step,
                step_number=1,
                total_steps=2,
                skill={},
                phase=None,
            )

            # Assert
            prompts_dir = tmp_project / ".vibecraft" / "prompts"
            assert prompts_dir.exists()
            prompt_files = list(prompts_dir.glob("*.md"))
            assert len(prompt_files) > 0


class TestRunStepErrorHandling:
    """Tests for step error handling."""

    def test_runStep_returnsFalse_whenAdapterRaisesRuntimeError(
        self, tmp_project: Path
    ) -> None:
        """_run_step returns False when adapter.call raises RuntimeError."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher"}

        with patch.object(runner.adapter, "call", side_effect=RuntimeError("Failed")):
            with patch.object(runner, "_handle_error", return_value=False) as mock_error:
                # Act
                result = runner._run_step(
                    step=step,
                    step_number=1,
                    total_steps=2,
                    skill={},
                    phase=None,
                    retry_count=0,
                )

                # Assert
                assert result is False
                mock_error.assert_called_once()

    def test_runStep_callsHandleError_whenAdapterFails(
        self, tmp_project: Path
    ) -> None:
        """_run_step calls _handle_error when adapter.call fails."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher"}

        with patch.object(runner.adapter, "call", side_effect=RuntimeError("Failed")):
            with patch.object(runner, "_handle_error", return_value=False) as mock_error:
                # Act
                runner._run_step(
                    step=step,
                    step_number=1,
                    total_steps=2,
                    skill={},
                    phase=None,
                    retry_count=0,
                )

                # Assert
                mock_error.assert_called_once()


class TestRunStepWithHumanGate:
    """Tests for step execution with human approval gate."""

    def test_runStep_callsHumanGate_whenGateIsHumanApproval(
        self, tmp_project: Path
    ) -> None:
        """_run_step invokes _human_gate when step has gate=human_approval."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {
            "agent": "researcher",
            "gate": "human_approval",
            "output": "docs/test.md",
        }

        with patch.object(runner.adapter, "call", return_value="# Response"):
            with patch.object(runner, "_human_gate", return_value=True) as mock_gate:
                # Act
                runner._run_step(
                    step=step,
                    step_number=1,
                    total_steps=2,
                    skill={},
                    phase=None,
                )

                # Assert
                mock_gate.assert_called_once()

    def test_runStep_continuesWithoutGate_whenGateNotSpecified(
        self, tmp_project: Path
    ) -> None:
        """_run_step returns True without gate when gate is not specified."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {
            "agent": "researcher",
            "output": "docs/test.md",
        }

        with patch.object(runner.adapter, "call", return_value="# Response"):
            # Act
            result = runner._run_step(
                step=step,
                step_number=1,
                total_steps=2,
                skill={},
                phase=None,
            )

            # Assert
            assert result is True


class TestHumanGateApproval:
    """Tests for human gate approval scenarios."""

    def test_humanGate_returnsTrue_whenUserInputsYes(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate returns True when user inputs 'y' or 'yes'."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        monkeypatch.setattr("builtins.input", lambda prompt: "y")

        # Act
        result = runner._human_gate(
            step={},
            step_number=1,
            total_steps=2,
            skill={},
            phase=None,
            response="# Response",
            output_path=None,
            retry_count=0,
            max_retries=3,
        )

        # Assert
        assert result is True

    def test_humanGate_returnsTrue_whenUserInputsEmpty(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate returns True when user inputs empty string (default approve)."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        monkeypatch.setattr("builtins.input", lambda prompt: "")

        # Act
        result = runner._human_gate(
            step={},
            step_number=1,
            total_steps=2,
            skill={},
            phase=None,
            response="# Response",
            output_path=None,
            retry_count=0,
            max_retries=3,
        )

        # Assert
        assert result is True

    def test_humanGate_returnsFalse_whenUserInputsNo(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate returns False when user inputs 'n' or 'no'."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        monkeypatch.setattr("builtins.input", lambda prompt: "n")

        # Act
        result = runner._human_gate(
            step={},
            step_number=1,
            total_steps=2,
            skill={},
            phase=None,
            response="# Response",
            output_path=None,
            retry_count=0,
            max_retries=3,
        )

        # Assert
        assert result is False


class TestHumanGateRetry:
    """Tests for human gate retry functionality."""

    def test_humanGate_retriesStep_whenUserInputsRetry(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate calls _run_step again when user inputs 'r' for retry."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher"}
        input_sequence = iter(["r", "y"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(input_sequence))

        with patch.object(runner.adapter, "call", return_value="# Response"):
            with patch.object(runner, "_run_step", return_value=True) as mock_run:
                # Act
                runner._human_gate(
                    step=step,
                    step_number=1,
                    total_steps=2,
                    skill={},
                    phase=None,
                    response="# Response",
                    output_path=None,
                    retry_count=0,
                    max_retries=3,
                )

                # Assert
                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs["retry_count"] == 1

    def test_humanGate_rejects_whenRetryExceedsMaxRetries(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate returns False when retry_count >= max_retries."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        monkeypatch.setattr("builtins.input", lambda prompt: "r")

        # Act
        result = runner._human_gate(
            step={},
            step_number=1,
            total_steps=2,
            skill={},
            phase=None,
            response="# Response",
            output_path=None,
            retry_count=3,
            max_retries=3,
        )

        # Assert
        assert result is False


class TestHumanGateEdit:
    """Tests for human gate edit functionality."""

    def test_humanGate_opensEditor_whenUserInputsEdit(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate opens editor when user inputs 'e'."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        output_path = tmp_project / "docs" / "test.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Original Content")

        monkeypatch.setattr("builtins.input", lambda prompt: "e")
        monkeypatch.setenv("EDITOR", "test_editor")

        with patch("vibecraft.modes.simple.runner.subprocess.run") as mock_run:
            # Act
            result = runner._human_gate(
                step={},
                step_number=1,
                total_steps=2,
                skill={},
                phase=None,
                response="# Response",
                output_path=output_path,
                retry_count=0,
                max_retries=3,
            )

            # Assert
            assert result is True
            mock_run.assert_called_once_with(["test_editor", str(output_path)])

    def test_humanGate_usesDefaultEditor_whenEnvNotSet(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate uses 'nano' as default editor when EDITOR not set."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        output_path = tmp_project / "docs" / "test.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Content")

        monkeypatch.setattr("builtins.input", lambda prompt: "e")
        monkeypatch.delenv("EDITOR", raising=False)
        monkeypatch.delenv("VISUAL", raising=False)

        with patch("vibecraft.modes.simple.runner.subprocess.run") as mock_run:
            # Act
            runner._human_gate(
                step={},
                step_number=1,
                total_steps=2,
                skill={},
                phase=None,
                response="# Response",
                output_path=output_path,
                retry_count=0,
                max_retries=3,
            )

            # Assert
            mock_run.assert_called_once_with(["nano", str(output_path)])


class TestHumanGateInterrupt:
    """Tests for human gate interrupt handling."""

    def test_humanGate_returnsFalse_whenKeyboardInterrupt(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate returns False when user presses Ctrl+C."""
        # Arrange
        runner = SimpleRunner(tmp_project)

        def raise_interrupt(prompt: str) -> None:
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", raise_interrupt)

        # Act
        result = runner._human_gate(
            step={},
            step_number=1,
            total_steps=2,
            skill={},
            phase=None,
            response="# Response",
            output_path=None,
            retry_count=0,
            max_retries=3,
        )

        # Assert
        assert result is False

    def test_humanGate_returnsFalse_whenEOFError(
        self, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_human_gate returns False when EOFError occurs."""
        # Arrange
        runner = SimpleRunner(tmp_project)

        def raise_eof(prompt: str) -> None:
            raise EOFError()

        monkeypatch.setattr("builtins.input", raise_eof)

        # Act
        result = runner._human_gate(
            step={},
            step_number=1,
            total_steps=2,
            skill={},
            phase=None,
            response="# Response",
            output_path=None,
            retry_count=0,
            max_retries=3,
        )

        # Assert
        assert result is False


class TestBuildStepPrompt:
    """Tests for prompt building functionality."""

    def test_buildStepPrompt_includesAgentPrompt_whenAgentFileExists(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt includes agent system prompt from file."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher", "description": "Test task"}
        skill = {"name": "Research Skill"}

        agent_file = tmp_project / ".vibecraft" / "agents" / "researcher.md"
        agent_file.write_text("You are a researcher agent.")

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=None)

        # Assert
        assert "You are a researcher agent." in prompt

    def test_buildStepPrompt_includesContext_whenContextFileExists(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt includes project context from context.md."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher"}
        skill = {"name": "Test"}

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=None)

        # Assert
        assert "Project Context" in prompt or "Tower Defense" in prompt

    def test_buildStepPrompt_includesStack_whenStackFileExists(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt includes stack information."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "researcher"}
        skill = {"name": "Test"}

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=None)

        # Assert
        assert "Stack" in prompt

    def test_buildStepPrompt_includesResearch_forEarlyPhaseAgents(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt includes research.md for researcher/architect/planner."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "architect"}
        skill = {"name": "Design Skill"}

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=None)

        # Assert
        assert "Research" in prompt

    def test_buildStepPrompt_excludesResearch_forImplementationAgents(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt excludes research.md for implementer/tdd_writer."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "implementer"}
        skill = {"name": "Implement Skill"}

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=None)

        # Assert - research should not be included for implementer
        assert "## Research" not in prompt

    def test_buildStepPrompt_includesArchitecture_forImplementationAgents(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt includes architecture.md for implementer/tdd_writer."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "implementer"}
        skill = {"name": "Implement"}

        arch_file = tmp_project / "docs" / "design" / "architecture.md"
        arch_file.parent.mkdir(parents=True, exist_ok=True)
        arch_file.write_text("# System Architecture")

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=None)

        # Assert
        assert "Architecture" in prompt

    def test_buildStepPrompt_includesPhasePlan_whenPhaseSpecified(
        self, tmp_project: Path
    ) -> None:
        """_build_step_prompt includes phase plan when phase number provided."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        step = {"agent": "implementer"}
        skill = {"name": "Implement"}

        plan_file = tmp_project / "docs" / "plans" / "phase_1.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        plan_file.write_text("# Phase 1 Implementation Plan")

        # Act
        prompt = runner._build_step_prompt(step, skill, phase=1)

        # Assert
        assert "Phase 1" in prompt
        assert "Plan" in prompt


class TestRunSkill:
    """Tests for full skill execution."""

    def test_run_executesAllSteps_whenSkillHasMultipleSteps(
        self, tmp_project: Path
    ) -> None:
        """run() executes all steps in the skill sequentially."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        skill = {
            "name": "Multi-Step Skill",
            "steps": [
                {"agent": "researcher", "output": "docs/step1.md"},
                {"agent": "architect", "output": "docs/step2.md"},
            ],
        }

        with patch.object(runner, "_load_skill", return_value=skill):
            with patch.object(runner.adapter, "call", return_value="# Response"):
                # Act
                runner.run("multi_step")

                # Assert
                assert (tmp_project / "docs" / "step1.md").exists()
                assert (tmp_project / "docs" / "step2.md").exists()

    def test_run_aborts_whenStepReturnsFalse(
        self, tmp_project: Path
    ) -> None:
        """run() aborts execution when any step returns False."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        skill = {
            "name": "Failing Skill",
            "steps": [
                {"agent": "researcher", "output": "docs/step1.md"},
                {"agent": "architect", "output": "docs/step2.md"},
            ],
        }

        # Mock _run_step to fail on second call
        call_count = [0]

        def run_step_mock(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First step succeeds - create file manually
                output_path = tmp_project / "docs" / "step1.md"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text("# Step 1")
                return True
            return False

        with patch.object(runner, "_load_skill", return_value=skill):
            with patch.object(runner, "_run_step", side_effect=run_step_mock):
                # Act
                runner.run("failing_skill")

                # Assert - second file should not be created
                assert (tmp_project / "docs" / "step1.md").exists()
                assert not (tmp_project / "docs" / "step2.md").exists()

    def test_run_updatesManifest_whenSkillCompletes(
        self, tmp_project: Path
    ) -> None:
        """run() calls complete_skill on ContextManager when all steps succeed."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        skill = {
            "name": "Test Skill",
            "steps": [{"agent": "researcher", "output": "docs/out.md"}],
        }

        with patch.object(runner, "_load_skill", return_value=skill):
            with patch.object(runner.adapter, "call", return_value="# Response"):
                with patch.object(
                    runner.ctx_manager, "complete_skill"
                ) as mock_complete:
                    # Act
                    runner.run("test_skill")

                    # Assert
                    mock_complete.assert_called_once_with("test_skill", None)

    def test_run_returnsEarly_whenSkillNotFound(
        self, tmp_project: Path
    ) -> None:
        """run() returns immediately when skill file not found."""
        # Arrange
        runner = SimpleRunner(tmp_project)

        with patch.object(runner, "_load_skill", return_value=None):
            # Act - should not raise
            runner.run("nonexistent_skill")

            # Assert - no exception, just early return


class TestExtractFilesFromResponse:
    """Tests for file extraction from LLM response."""

    def test_extractFilesFromResponse_extractsFileWithHeading(
        self, tmp_project: Path
    ) -> None:
        """_extract_files_from_response extracts file from ### heading format."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        response = """### src/main.py
```python
print("Hello")
```
"""
        output_dir = tmp_project / "src"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Act
        created = runner._extract_files_from_response(response, output_dir)

        # Assert
        assert len(created) == 1
        assert created[0].name == "main.py"
        assert 'print("Hello")' in created[0].read_text()

    def test_extractFilesFromResponse_extractsFileWithBackticks(
        self, tmp_project: Path
    ) -> None:
        """_extract_files_from_response extracts file from **`filename`** format."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        response = """**`src/utils.py`**
```python
def helper(): pass
```
"""
        output_dir = tmp_project / "src"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Act
        created = runner._extract_files_from_response(response, output_dir)

        # Assert
        assert len(created) == 1
        assert created[0].name == "utils.py"

    def test_extractFilesFromResponse_createsFallbackFile_whenNoFilesFound(
        self, tmp_project: Path
    ) -> None:
        """_extract_files_from_response creates output.md when no files parsed."""
        # Arrange
        runner = SimpleRunner(tmp_project)
        response = "# Just plain text, no code blocks"
        output_dir = tmp_project / "docs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Act
        created = runner._extract_files_from_response(response, output_dir)

        # Assert
        assert len(created) == 1
        assert created[0].name == "output.md"
        assert "Just plain text" in created[0].read_text()
