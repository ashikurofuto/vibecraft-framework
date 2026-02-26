"""
Vibecraft setup with Windows PATH configuration.

This setup script ensures that the Scripts directory is added to PATH
on Windows for global command availability.
"""

import os
import sys
import subprocess
from pathlib import Path

# Only import setuptools when needed to avoid conflicts
try:
    from setuptools import setup, find_packages
except ImportError:
    # If setuptools is not available, install it first
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    from setuptools import setup, find_packages


def get_scripts_path():
    """Get the scripts installation path."""
    import sysconfig
    
    # On Windows, scripts go to Scripts/ directory
    if sys.platform == "win32":
        # Get the base directory for the Python installation
        base = sys.prefix
        scripts_dir = Path(base) / "Scripts"
        return str(scripts_dir)
    return None


def add_to_windows_path(path_to_add):
    """Add path to Windows user PATH using setx."""
    if not path_to_add:
        return False
    
    try:
        # Use setx to add to user PATH (safer than registry manipulation)
        # First get current PATH
        current_path = os.environ.get("PATH", "")
        
        # Check if already in PATH
        if path_to_add.lower() in current_path.lower():
            return True
        
        # Build new PATH
        new_path = current_path
        if new_path and not new_path.endswith(";"):
            new_path += ";"
        new_path += path_to_add
        
        # Use setx to persist the PATH (user-level)
        result = subprocess.run(
            ["setx", "PATH", new_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n[post-install] Added {path_to_add} to PATH")
            print("[post-install] Restart your terminal to use 'vibecraft' globally")
            return True
        else:
            print(f"\n[post-install] Warning: Could not modify PATH automatically")
            return False
            
    except Exception as e:
        print(f"\n[post-install] Error: {e}")
        return False


# Custom install command
class InstallCommand:
    """Wrapper to handle post-install configuration."""
    
    @staticmethod
    def run_post_install():
        """Run post-installation configuration."""
        if sys.platform == "win32":
            scripts_path = get_scripts_path()
            if scripts_path:
                add_to_windows_path(scripts_path)


def run_setup():
    """Execute the setup."""
    setup(
        name="vibecraft",
        version="0.3.0",
        description="Agent-driven development framework. Craft your project from a research idea.",
        long_description=Path("README.md").read_text(encoding="utf-8"),
        long_description_content_type="text/markdown",
        author="Vibecraft Team",
        packages=find_packages(where="."),
        python_requires=">=3.10",
        install_requires=[
            "click>=8.1",
            "jinja2>=3.1",
            "pyyaml>=6.0",
            "rich>=13.0",
            "pyperclip>=1.8",
        ],
        extras_require={
            "test": [
                "pytest>=8.0",
                "pytest-cov>=4.0",
            ],
        },
        entry_points={
            "console_scripts": [
                "vibecraft=vibecraft.main:main",
            ],
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: 3.14",
        ],
    )
    
    # Run post-install if installing
    if "install" in sys.argv or "develop" in sys.argv:
        InstallCommand.run_post_install()


if __name__ == "__main__":
    run_setup()
