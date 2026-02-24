"""
vibecraft doctor — environment and project diagnostics.

Checks everything that could silently break before a user runs a skill.
"""

import importlib
import json
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

_REQUIRED_PACKAGES = [
    "click",
    "jinja2",
    "yaml",       # pyyaml
    "rich",
    "pyperclip",
]

_OPTIONAL_PACKAGES = {
    "pyperclip": "clipboard copy/paste (context --copy)",
}


def run_doctor(project_root: Path | None = None):
    console.print("\n[bold cyan]Vibecraft Doctor[/bold cyan]\n")

    all_ok = True
    all_ok &= _check_python_version()
    all_ok &= _check_packages()
    all_ok &= _check_qwen_cli()

    if project_root:
        all_ok &= _check_project_structure(project_root)
        all_ok &= _check_manifest(project_root)

    console.print()
    if all_ok:
        console.print("[bold green]✓ Everything looks good![/bold green]\n")
    else:
        console.print(
            "[bold yellow]⚠ Some issues found — see above.[/bold yellow]\n"
        )

    return all_ok


# ------------------------------------------------------------------


def _check_python_version() -> bool:
    required = (3, 10)
    current  = sys.version_info[:2]
    ok       = current >= required

    _row(
        "Python version",
        f"{current[0]}.{current[1]}",
        ok,
        f"Required ≥ {required[0]}.{required[1]}",
    )
    return ok


def _check_packages() -> bool:
    all_ok = True
    for pkg in _REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            _row("Package", pkg, True)
        except ImportError:
            install_name = "pyyaml" if pkg == "yaml" else pkg
            _row("Package", pkg, False, f"pip install {install_name}")
            all_ok = False
    return all_ok


def _check_qwen_cli() -> bool:
    import os
    cmd = os.environ.get("VIBECRAFT_QWEN_CMD", "qwen")
    found = shutil.which(cmd) is not None

    if found:
        _row("Qwen CLI", cmd, True)
    else:
        _row(
            "Qwen CLI",
            cmd,
            False,
            "Not found on PATH. Set VIBECRAFT_BACKEND=clipboard for dry-run mode.",
            warning_only=True,   # not fatal if using clipboard backend
        )
    return True   # Qwen is optional if using another backend


def _check_project_structure(root: Path) -> bool:
    required_paths = [
        root / ".vibecraft" / "manifest.json",
        root / ".vibecraft" / "agents",
        root / ".vibecraft" / "skills",
        root / "docs" / "research.md",
        root / "docs" / "stack.md",
        root / "docs" / "context.md",
        root / "src" / "tests",
    ]
    all_ok = True
    for p in required_paths:
        exists = p.exists()
        _row("Path", str(p.relative_to(root)), exists)
        if not exists:
            all_ok = False
    return all_ok


def _check_manifest(root: Path) -> bool:
    manifest_path = root / ".vibecraft" / "manifest.json"
    if not manifest_path.exists():
        return True  # already reported above

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _row("Manifest JSON", "manifest.json", False, f"Invalid JSON: {e}")
        return False

    required_keys = [
        "project_name", "project_type", "created_at",
        "stack", "agents", "skills", "current_phase",
        "phases", "phases_completed",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        _row(
            "Manifest keys",
            "manifest.json",
            False,
            f"Missing keys: {', '.join(missing)}",
        )
        return False

    _row("Manifest JSON", "manifest.json", True)
    return True


# ------------------------------------------------------------------


def _row(
    category: str,
    item: str,
    ok: bool,
    note: str = "",
    warning_only: bool = False,
):
    icon   = "[green]✓[/green]" if ok else ("[yellow]⚠[/yellow]" if warning_only else "[red]✗[/red]")
    status = "[green]OK[/green]" if ok else ("[yellow]WARN[/yellow]" if warning_only else "[red]FAIL[/red]")
    line   = f"  {icon}  [{category}] {item}  →  {status}"
    if note:
        line += f"  [dim]{note}[/dim]"
    console.print(line)
