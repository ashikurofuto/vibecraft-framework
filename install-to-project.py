#!/usr/bin/env python3
"""
Vibecraft installer for local project installation.

This script installs vibecraft into a local .vibecraft-venv/ directory
within your project, allowing you to have different versions per project.

Usage:
    python install-to-project.py [project_directory]
    
If no directory is specified, installs to the current directory.

After installation:
    - Run: .vibecraft-venv/Scripts/activate  (to activate venv)
    - Or use: .vibecraft-venv/Scripts/vibecraft  (direct command)
    - Or use launcher: vibecraft-local.bat (if created)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def _setup_windows_encoding():
    """Configure UTF-8 encoding for Windows consoles."""
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, UnicodeError):
            pass
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, UnicodeError):
            pass


_setup_windows_encoding()


def get_script_dir():
    """Get the directory where this script is located."""
    return Path(__file__).parent.resolve()


def create_virtualenv(venv_path):
    """Create a virtual environment at the specified path."""
    print(f"\n[1/4] Creating virtual environment at {venv_path}...")
    
    try:
        # Use built-in venv module
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ Failed to create virtual environment:")
            print(result.stderr)
            return False
        
        print("✓ Virtual environment created")
        return True
        
    except Exception as e:
        print(f"✗ Error creating virtual environment: {e}")
        return False


def install_to_venv(venv_path, package_path):
    """Install vibecraft package into the virtual environment."""
    print(f"\n[2/4] Installing vibecraft into virtual environment...")
    
    # Get pip path in venv
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"
    
    result = subprocess.run(
        [str(pip_path), "install", "-e", str(package_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"✗ Installation failed:")
        print(result.stderr)
        return False
    
    print("✓ Package installed successfully")
    return True


def create_launcher(project_dir, venv_path):
    """Create a launcher batch file for easy access."""
    print(f"\n[3/4] Creating launcher scripts...")
    
    # Create vibecraft-local.bat
    bat_path = project_dir / "vibecraft-local.bat"
    
    if sys.platform == "win32":
        vibecraft_exe = venv_path / "Scripts" / "vibecraft.exe"
        bat_content = f"""@echo off
REM Vibecraft Local Launcher
REM This runs vibecraft from the local .vibecraft-venv/ installation

"{vibecraft_exe}" %*
"""
    else:
        vibecraft_exe = venv_path / "bin" / "vibecraft"
        bat_content = f"""#!/bin/bash
# Vibecraft Local Launcher
# This runs vibecraft from the local .vibecraft-venv/ installation

"{vibecraft_exe}" "$@"
"""
    
    bat_path.write_text(bat_content, encoding="utf-8")
    print(f"✓ Created launcher: {bat_path}")
    
    # Create activate script reminder
    if sys.platform == "win32":
        print(f"✓ You can also run: .vibecraft-venv\\Scripts\\activate")
    else:
        print(f"✓ You can also run: source .vibecraft-venv/bin/activate")
    
    return True


def print_usage_instructions(project_dir):
    """Print usage instructions for the user."""
    print("\n" + "=" * 60)
    print("  Local Installation Complete!")
    print("=" * 60)
    print(f"\nVibecraft has been installed locally in:")
    print(f"  {project_dir / '.vibecraft-venv'}")
    print("\nUsage options:")
    print("\n  Option 1: Use the launcher (recommended)")
    print(f"    {project_dir / 'vibecraft-local.bat'}")
    print("    Example: vibecraft-local.bat --help")
    print("\n  Option 2: Activate the virtual environment")
    if sys.platform == "win32":
        print(f"    .vibecraft-venv\\Scripts\\activate")
        print("    Then run: vibecraft --help")
    else:
        print(f"    source .vibecraft-venv/bin/activate")
        print("    Then run: vibecraft --help")
    print("\n  Option 3: Run directly")
    if sys.platform == "win32":
        print(f"    .vibecraft-venv\\Scripts\\vibecraft --help")
    else:
        print(f"    .vibecraft-venv/bin/vibecraft --help")
    print("\nQuick start:")
    print("  vibecraft-local.bat doctor")
    print("  vibecraft-local.bat init -r research.md -s stack.md")
    print()


def main():
    """Main installation routine."""
    print("=" * 60)
    print("  Vibecraft Local Installer (Windows)")
    print("  Install vibecraft into your project directory")
    print("=" * 60)
    
    # Determine target directory
    if len(sys.argv) > 1:
        project_dir = Path(sys.argv[1]).resolve()
    else:
        project_dir = Path.cwd()
    
    print(f"\nTarget project directory: {project_dir}")
    
    if not project_dir.exists():
        print(f"✗ Directory does not exist: {project_dir}")
        sys.exit(1)
    
    # Check if already installed
    venv_path = project_dir / ".vibecraft-venv"
    if venv_path.exists():
        print(f"\n⚠ Local installation already exists at: {venv_path}")
        try:
            response = input("  Reinstall? This will overwrite the existing installation. [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nInstallation cancelled.")
            sys.exit(0)
        
        if response not in ("y", "yes"):
            print("Installation cancelled.")
            sys.exit(0)
        
        # Remove existing installation
        print("Removing existing installation...")
        try:
            shutil.rmtree(venv_path)
        except Exception as e:
            print(f"✗ Failed to remove existing installation: {e}")
            sys.exit(1)
    
    # Get package path (parent directory where vibecraft-framework/ is)
    script_dir = get_script_dir()
    package_path = script_dir  # install.py is in vibecraft-framework/
    
    if not (package_path / "pyproject.toml").exists():
        print(f"✗ vibecraft-framework not found at: {package_path}")
        sys.exit(1)
    
    # Step 1: Create virtual environment
    if not create_virtualenv(venv_path):
        print("\n✗ Installation aborted.")
        sys.exit(1)
    
    # Step 2: Install package into venv
    if not install_to_venv(venv_path, package_path):
        print("\n✗ Installation aborted.")
        sys.exit(1)
    
    # Step 3: Create launcher
    if not create_launcher(project_dir, venv_path):
        print("\n⚠ Warning: Launcher creation failed, but installation is usable.")
    
    # Step 4: Print instructions
    print_usage_instructions(project_dir)


if __name__ == "__main__":
    main()
