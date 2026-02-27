"""
Tests for BaseAdapter abstract base class.

Tests verify that BaseAdapter properly defines the adapter interface
and enforces implementation requirements.
"""

import pytest
from pathlib import Path

from vibecraft.adapters.base_adapter import BaseAdapter


class TestBaseAdapterABC:
    """Tests for BaseAdapter abstract base class."""

    def test_base_adapter_cannot_instantiate(self):
        """BaseAdapter cannot be instantiated directly (ABC)."""
        # Act & Assert
        with pytest.raises(TypeError, match="abstract class"):
            BaseAdapter()

    def test_base_adapter_has_abstract_method(self):
        """BaseAdapter defines call() as abstract method."""
        # Assert
        assert "call" in BaseAdapter.__abstractmethods__

    def test_concrete_adapter_implementation(self):
        """Concrete implementation must implement call() method."""
        # Arrange - incomplete implementation (no call method)
        class IncompleteAdapter(BaseAdapter):
            pass

        # Act & Assert
        with pytest.raises(TypeError, match="abstract method"):
            IncompleteAdapter()

    def test_complete_adapter_implementation(self):
        """Complete implementation can be instantiated."""
        # Arrange - complete implementation
        class CompleteAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return "Response"

        # Act
        adapter = CompleteAdapter()

        # Assert
        assert adapter is not None
        assert adapter.call("Test prompt") == "Response"

    def test_adapter_call_with_context_files(self):
        """Adapter call() accepts optional context_files parameter."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                if context_files:
                    return f"Processed {len(context_files)} files"
                return "No context"

        adapter = TestAdapter()

        # Act & Assert - with context files
        context = [Path("file1.txt"), Path("file2.txt")]
        assert adapter.call("Prompt", context_files=context) == "Processed 2 files"

        # Act & Assert - without context files
        assert adapter.call("Prompt") == "No context"

    def test_adapter_call_with_none_context_files(self):
        """Adapter call() handles None context_files."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return "OK"

        adapter = TestAdapter()

        # Act & Assert
        result = adapter.call("Prompt", context_files=None)
        assert result == "OK"

    def test_adapter_call_with_empty_context_files(self):
        """Adapter call() handles empty context_files list."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return f"Count: {len(context_files) if context_files else 0}"

        adapter = TestAdapter()

        # Act & Assert
        result = adapter.call("Prompt", context_files=[])
        assert result == "Count: 0"

    def test_adapter_call_return_type(self):
        """Adapter call() returns string."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return "String response"

        adapter = TestAdapter()

        # Act
        result = adapter.call("Prompt")

        # Assert
        assert isinstance(result, str)

    def test_adapter_call_receives_prompt(self):
        """Adapter call() receives the prompt argument."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return f"Received: {prompt}"

        adapter = TestAdapter()

        # Act
        result = adapter.call("Test prompt content")

        # Assert
        assert "Test prompt content" in result

    def test_adapter_call_receives_context_file_paths(self):
        """Adapter call() receives context file paths."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                if context_files:
                    return str(context_files[0])
                return "No files"

        adapter = TestAdapter()
        test_file = Path("tmp") / "test.txt"

        # Act
        result = adapter.call("Prompt", context_files=[test_file])

        # Assert - use os.path.sep for cross-platform compatibility
        import os
        assert f"tmp{os.path.sep}test.txt" in result or "tmp/test.txt" in result or "tmp\\test.txt" in result


class TestBaseAdapterSubclass:
    """Tests for BaseAdapter subclass behavior."""

    def test_subclass_inherits_from_base_adapter(self):
        """Subclass is instance of BaseAdapter."""
        # Arrange
        class MyAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return "OK"

        adapter = MyAdapter()

        # Assert
        assert isinstance(adapter, BaseAdapter)

    def test_subclass_can_override_call_behavior(self):
        """Subclass can implement custom call() behavior."""
        # Arrange
        class MockAdapter(BaseAdapter):
            def __init__(self, response: str = "Mock response"):
                self.response = response

            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return self.response

        # Act
        adapter1 = MockAdapter("Response 1")
        adapter2 = MockAdapter("Response 2")

        # Assert
        assert adapter1.call("Prompt") == "Response 1"
        assert adapter2.call("Prompt") == "Response 2"

    def test_subclass_can_add_additional_methods(self):
        """Subclass can add additional methods beyond call()."""
        # Arrange
        class ExtendedAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return "OK"

            def custom_method(self) -> str:
                return "Custom"

        adapter = ExtendedAdapter()

        # Assert
        assert adapter.call("Prompt") == "OK"
        assert adapter.custom_method() == "Custom"

    def test_subclass_can_have_init(self):
        """Subclass can have custom __init__."""
        # Arrange
        class ConfigurableAdapter(BaseAdapter):
            def __init__(self, api_key: str, timeout: int = 30):
                self.api_key = api_key
                self.timeout = timeout

            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return f"Using key {self.api_key[:4]}... timeout={self.timeout}"

        # Act
        adapter = ConfigurableAdapter("secret-key-123", timeout=60)

        # Assert
        result = adapter.call("Prompt")
        assert "secr" in result
        assert "timeout=60" in result


class TestBaseAdapterEdgeCases:
    """Tests for edge cases in BaseAdapter."""

    def test_adapter_handles_empty_prompt(self):
        """Adapter handles empty prompt string."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return f"Prompt length: {len(prompt)}"

        adapter = TestAdapter()

        # Act
        result = adapter.call("")

        # Assert
        assert "0" in result

    def test_adapter_handles_unicode_prompt(self):
        """Adapter handles Unicode in prompt."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return prompt

        adapter = TestAdapter()

        # Act
        result = adapter.call("Привет 世界 🌍")

        # Assert
        assert "Привет" in result
        assert "世界" in result

    def test_adapter_handles_very_long_prompt(self):
        """Adapter handles very long prompts."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return f"Received {len(prompt)} chars"

        adapter = TestAdapter()
        long_prompt = "A" * 100000

        # Act
        result = adapter.call(long_prompt)

        # Assert
        assert "100000" in result

    def test_adapter_handles_many_context_files(self):
        """Adapter handles many context files."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                return f"Files: {len(context_files) if context_files else 0}"

        adapter = TestAdapter()
        many_files = [Path(f"file{i}.txt") for i in range(100)]

        # Act
        result = adapter.call("Prompt", context_files=many_files)

        # Assert
        assert "100" in result

    def test_adapter_context_files_with_nested_paths(self):
        """Adapter handles context files with nested paths."""
        # Arrange
        class TestAdapter(BaseAdapter):
            def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
                if context_files:
                    return str(context_files[0])
                return "No files"

        adapter = TestAdapter()
        nested = Path("deep") / "nested" / "path" / "to" / "file.txt"

        # Act
        result = adapter.call("Prompt", context_files=[nested])

        # Assert - cross-platform path check
        assert "deep" in result
        assert "nested" in result
        assert "file.txt" in result
