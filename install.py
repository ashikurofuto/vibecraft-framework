#!/usr/bin/env python3
"""
Vibecraft installer for Windows.

This script installs vibecraft and ensures the Scripts directory
is added to PATH for global command availability.

Usage:
    python install.py

Fixes implemented (v0.4):
    - DEPLOY-001: Uses setx instead of winreg (more reliable)
    - DEPLOY-003: Verifies PATH addition success
    - DEPLOY-004: Provides command to refresh PATH in current session
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


def get_python_scripts_path():
    """Get the path where pip installs scripts."""
    import site
    import sysconfig

    # For Windows, scripts go to Scripts/ next to the Python installation
    python_path = Path(sys.executable)

    # Check if it's a Windows Store / Microsoft Store Python installation
    if "WindowsApps" in str(python_path):
        # Microsoft Store Python - use user scripts
        return Path(site.USER_BASE) / "Scripts"

    # Standard Python installation
    scripts_dir = python_path.parent / "Scripts"
    if scripts_dir.exists():
        return scripts_dir

    # Fallback: try site-packages location
    for path in sys.path:
        if "site-packages" in path:
            scripts_dir = Path(path).parent / "Scripts"
            if scripts_dir.exists():
                return scripts_dir

    return scripts_dir


def is_path_in_env(path_to_check):
    """Check if path is already in PATH environment variable."""
    path_str = str(path_to_check)
    current_path = os.environ.get("PATH", "")
    return path_str.lower() in current_path.lower()


def add_to_user_path_with_setx(path_to_add):
    """
    Add a path to the user's PATH environment variable using setx.
    
    DEPLOY-001 FIX: Uses setx instead of winreg for better reliability.
    setx works without admin rights and is more consistent across Windows versions.
    
    Returns:
        bool: True if successful, False otherwise
    """
    path_str = str(path_to_add)
    
    try:
        # First get current PATH from registry
        result = subprocess.run(
            ["reg", "query", "HKCU\\Environment", "/v", "PATH"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse existing PATH
            for line in result.stdout.splitlines():
                if "PATH" in line and "REG" in line:
                    # Extract PATH value
                    parts = line.split("REG_EXPAND_SZ")
                    if len(parts) > 1:
                        current_path = parts[1].strip()
                        break
            else:
                current_path = ""
        else:
            current_path = ""
        
        # Check if already in PATH
        if path_str.lower() in current_path.lower():
            print(f"✓ Path already in user PATH: {path_str}")
            return True
        
        # Build new PATH
        new_path = current_path
        if new_path and not new_path.endswith(";"):
            new_path += ";"
        new_path += path_str
        
        # Use setx to persist the PATH (user-level)
        # DEPLOY-001 FIX: setx is more reliable than winreg
        result = subprocess.run(
            ["setx", "PATH", new_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Added to user PATH: {path_str}")
            return True
        else:
            print(f"✗ setx failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error modifying PATH: {e}")
        return False


def verify_path_added(path_to_check):
    """
    Verify that path was added to PATH environment variable.
    
    DEPLOY-003 FIX: Explicitly verify PATH addition success.
    
    Note: setx changes don't affect current process, so we check
    by reading from registry.
    """
    path_str = str(path_to_check).lower()
    
    try:
        result = subprocess.run(
            ["reg", "query", "HKCU\\Environment", "/v", "PATH"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return path_str in result.stdout.lower()
        return False
    except Exception:
        return False


def print_path_refresh_instructions():
    """
    Print instructions for refreshing PATH in current session.
    
    DEPLOY-004 FIX: Provide commands to refresh PATH without restart.
    """
    print("\n" + "=" * 60)
    print("  PATH Update Instructions")
    print("=" * 60)
    print("\n⚠ PATH has been updated, but your current terminal session")
    print("  needs to be refreshed to recognize the changes.\n")
    print("Choose one of the following options:\n")
    print("  Option 1: Restart your terminal (recommended)")
    print("  Option 2: Run this command in PowerShell:")
    print("    $env:PATH = [System.Environment]::GetEnvironmentVariable(")
    print("        \"PATH\", \"User\")")
    print("  Option 3: Run this command in CMD:")
    print("    setx PATH \"\"  # Then close and reopen terminal")
    print("\nAfter refreshing, verify with:")
    print("  vibecraft --help")


def install_package():
    """Install the vibecraft package using pip."""
    print("\n[1/2] Installing vibecraft package...")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"✗ Installation failed:")
        print(result.stderr)
        return False

    print("✓ Package installed successfully")
    return True


def main():
    """Main installation routine."""
    print("=" * 60)
    print("  Vibecraft Installer (Windows)")
    print("  v0.4 - Improved PATH reliability")
    print("=" * 60)

    # Step 1: Install package
    if not install_package():
        print("\n✗ Installation aborted.")
        sys.exit(1)

    # Step 2: Add Scripts to PATH
    scripts_path = get_python_scripts_path()

    print(f"\n[2/2] Configuring PATH...")
    print(f"Scripts directory: {scripts_path}")

    if not scripts_path.exists():
        print(f"✗ Scripts directory not found: {scripts_path}")
        print("\nManual installation required:")
        print(f"  1. Add '{scripts_path}' to your PATH")
        print(f"  2. Restart your terminal")
        sys.exit(1)

    if is_path_in_env(scripts_path):
        print(f"✓ Scripts directory already in PATH")
        path_added = True
    else:
        # DEPLOY-001 FIX: Use setx instead of winreg
        path_added = add_to_user_path_with_setx(scripts_path)
        
        # DEPLOY-003 FIX: Verify PATH was actually added
        if path_added:
            verified = verify_path_added(scripts_path)
            if not verified:
                print(f"\n⚠ Warning: PATH modification may not have been saved.")
                print(f"  Please verify manually or restart terminal.")
                path_added = False

    # Verify installation
    print("\n" + "=" * 60)
    if path_added:
        print("  Installation Complete!")
    else:
        print("  Installation Complete (with warnings)")
    print("=" * 60)
    
    if path_added:
        # DEPLOY-004 FIX: Provide refresh instructions
        print_path_refresh_instructions()
    else:
        print("\n⚠ PATH was not updated automatically.")
        print(f"  Please add '{scripts_path}' to your PATH manually.")
        print("\nSteps:")
        print("  1. Press Win+R, type 'sysdm.cpl', press Enter")
        print("  2. Click 'Environment Variables'")
        print(f"  3. Add '{scripts_path}' to user PATH")
        print("  4. Restart terminal")
    
    print("\nQuick start after PATH is configured:")
    print("  vibecraft doctor              # Check environment")
    print("  vibecraft init -r research.md -s stack.md  # Initialize project")
    print()


if __name__ == "__main__":
    main()
