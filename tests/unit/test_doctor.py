"""Tests for doctor module."""

import pytest
from pathlib import Path
from vibecraft.doctor import run_doctor, _check_python_version, _check_packages


class TestCheckPythonVersion:
    """Tests for _check_python_version."""

    def test_returns_bool(self):
        """Should return boolean."""
        result = _check_python_version()
        assert isinstance(result, bool)

    def test_python_3_10_passes(self):
        """Python 3.10+ should pass."""
        import sys
        if sys.version_info >= (3, 10):
            assert _check_python_version() is True


class TestCheckPackages:
    """Tests for _check_packages."""

    def test_required_packages_installed(self, capsys):
        """Should pass when all required packages are installed."""
        result = _check_packages()
        # click, jinja2, yaml, rich, pyperclip should be installed
        assert result is True


class TestRunDoctor:
    """Tests for run_doctor."""

    def test_run_doctor_with_project(self, tmp_project, capsys):
        """Should run all checks with project root."""
        result = run_doctor(project_root=tmp_project)
        captured = capsys.readouterr()

        assert "Doctor" in captured.out
        assert isinstance(result, bool)

    def test_run_doctor_without_project(self, capsys):
        """Should run without project root."""
        result = run_doctor()
        captured = capsys.readouterr()

        assert "Doctor" in captured.out
        assert isinstance(result, bool)


class TestCheckProjectStructure:
    """Tests for _check_project_structure."""

    def test_valid_project_passes(self, tmp_project, capsys):
        """Valid project structure should pass."""
        from vibecraft.doctor import _check_project_structure
        result = _check_project_structure(tmp_project)
        assert result is True

    def test_missing_manifest_fails(self, tmp_path, capsys):
        """Missing manifest.json should fail."""
        from vibecraft.doctor import _check_project_structure
        result = _check_project_structure(tmp_path)
        assert result is False

    def test_missing_docs_fails(self, tmp_path, capsys):
        """Missing docs/ should fail."""
        vc_dir = tmp_path / ".vibecraft"
        vc_dir.mkdir()
        (vc_dir / "manifest.json").write_text("{}")

        from vibecraft.doctor import _check_project_structure
        result = _check_project_structure(tmp_path)
        assert result is False


class TestCheckManifest:
    """Tests for _check_manifest."""

    def test_valid_manifest_passes(self, tmp_project):
        """Valid manifest should pass."""
        from vibecraft.doctor import _check_manifest
        result = _check_manifest(tmp_project)
        assert result is True

    def test_invalid_json_fails(self, tmp_path):
        """Invalid JSON should fail."""
        vc_dir = tmp_path / ".vibecraft"
        vc_dir.mkdir()
        (vc_dir / "manifest.json").write_text("not valid json")

        from vibecraft.doctor import _check_manifest
        result = _check_manifest(tmp_path)
        assert result is False

    def test_missing_keys_fail(self, tmp_path):
        """Missing required keys should fail."""
        vc_dir = tmp_path / ".vibecraft"
        vc_dir.mkdir()
        (vc_dir / "manifest.json").write_text('{"foo": "bar"}')

        from vibecraft.doctor import _check_manifest
        result = _check_manifest(tmp_path)
        assert result is False
