"""Tests for Exporter module."""

import json
import zipfile
from pathlib import Path
from vibecraft.exporter import Exporter


class TestExportMarkdown:
    """Tests for export_markdown."""

    def test_creates_project_summary(self, tmp_project):
        """Should create docs/project_summary.md."""
        exporter = Exporter(tmp_project)
        path = exporter.export_markdown()

        assert path.exists()
        assert path.name == "project_summary.md"
        assert path.parent == tmp_project / "docs"

    def test_includes_project_name(self, tmp_project):
        """Should include project name in summary."""
        exporter = Exporter(tmp_project)
        path = exporter.export_markdown()

        content = path.read_text()
        assert "Tower Defense Game (Multiplayer)" in content

    def test_includes_research(self, tmp_project):
        """Should include research.md content."""
        exporter = Exporter(tmp_project)
        path = exporter.export_markdown()

        content = path.read_text()
        assert "## Research" in content or "Research" in content

    def test_includes_stack(self, tmp_project):
        """Should include stack.md content."""
        exporter = Exporter(tmp_project)
        path = exporter.export_markdown()

        content = path.read_text()
        assert "## Stack" in content or "Stack" in content


class TestExportZip:
    """Tests for export_zip."""

    def test_creates_zip_file(self, tmp_project):
        """Should create a zip file."""
        exporter = Exporter(tmp_project)
        path = exporter.export_zip()

        assert path.exists()
        assert path.suffix == ".zip"

    def test_zip_contains_docs(self, tmp_project):
        """Should include docs/ in zip."""
        exporter = Exporter(tmp_project)
        path = exporter.export_zip()

        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            assert any("docs/" in n for n in names)

    def test_zip_contains_manifest(self, tmp_project):
        """Should include manifest.json in zip."""
        exporter = Exporter(tmp_project)
        path = exporter.export_zip()

        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            assert any("manifest.json" in n for n in names)

    def test_zip_in_exports_dir(self, tmp_project):
        """Should create zip in exports/ directory."""
        exporter = Exporter(tmp_project)
        path = exporter.export_zip()

        # Should be in exports/ subdirectory
        assert "exports" in str(path.parent) or path.parent == tmp_project


class TestLoadManifest:
    """Tests for _load_manifest."""

    def test_loads_valid_manifest(self, tmp_project):
        """Should load valid manifest.json."""
        exporter = Exporter(tmp_project)
        manifest = exporter._load_manifest()

        assert isinstance(manifest, dict)
        assert "project_name" in manifest

    def test_returns_empty_for_missing(self, tmp_path):
        """Should return empty dict for missing manifest."""
        exporter = Exporter(tmp_path)
        manifest = exporter._load_manifest()

        assert manifest == {}
