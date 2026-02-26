#!/usr/bin/env python3
"""
Configure Vibecraft for global access.

This script adds the Python Scripts directory to your PATH
so you can use 'vibecraft' command from anywhere.

Usage:
    python configure_path.py
"""

import os
import sys
import subprocess
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


def get_scripts_path():
    """Get the Python Scripts directory."""
    python_path = Path(sys.executable)
    
    # Standard installation
    scripts_dir = python_path.parent / "Scripts"
    if scripts_dir.exists():
        return scripts_dir
    
    # Try sysconfig
    import sysconfig
    schemes = sysconfig.get_scheme_names()
    for scheme in schemes:
        try:
            scripts = Path(sysconfig.get_path("scripts", scheme=scheme))
            if scripts.exists():
                return scripts
        except (KeyError, OSError):
            continue
    
    return scripts_dir


def is_in_path(path_to_check):
    """Check if path is already in PATH."""
    path_str = str(path_to_check).lower()
    current_path = os.environ.get("PATH", "").lower()
    return path_str in current_path


def add_to_user_path(path_to_add):
    """Add path to user PATH using setx (Windows)."""
    if sys.platform != "win32":
        print("This script is for Windows only.")
        return False
    
    path_str = str(path_to_add)
    
    # Check if already in PATH
    if is_in_path(path_to_add):
        print(f"✓ Already in PATH: {path_str}")
        return True
    
    # Get current PATH from registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error reading PATH: {e}")
        return False
    
    # Build new PATH
    new_path = current_path
    if new_path and not new_path.endswith(";"):
        new_path += ";"
    new_path += path_str
    
    # Use setx to persist
    result = subprocess.run(["setx", "PATH", new_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Added to PATH: {path_str}")
        return True
    else:
        print(f"✗ Failed to add to PATH: {result.stderr}")
        return False


def main():
    print("=" * 60)
    print("  Vibecraft PATH Configuration")
    print("=" * 60)
    
    scripts_path = get_scripts_path()
    print(f"\nScripts directory: {scripts_path}")
    
    if not scripts_path.exists():
        print(f"✗ Scripts directory not found: {scripts_path}")
        sys.exit(1)
    
    if is_in_path(scripts_path):
        print("✓ Scripts directory is already in PATH")
        print("\nYou can now use 'vibecraft' from any terminal!")
    else:
        print("Adding Scripts directory to PATH...")
        if add_to_user_path(scripts_path):
            print("\n⚠ IMPORTANT: Restart your terminal for changes to take effect.")
            print("   After restart, 'vibecraft' will be available globally.")
        else:
            print("\nManual configuration required:")
            print(f"  1. Add '{scripts_path}' to your PATH")
            print(f"  2. Restart your terminal")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  Configuration Complete!")
    print("=" * 60)
    print("\nAfter restarting your terminal:")
    print("  vibecraft --help")
    print("  vibecraft doctor")
    print()


if __name__ == "__main__":
    main()
