# Vibecraft Installation Guide

## Quick Install (Windows)

### Method 1: Global Install (One-Click)

1. Navigate to the `vibecraft-framework` folder
2. Double-click `install.bat`
3. Wait for installation to complete
4. **Refresh your PATH** (see options below)
5. Verify: `vibecraft --help`

### Method 2: Global Install (PowerShell/CMD)

```powershell
# PowerShell
cd vibecraft-framework
.\install.ps1
```

```cmd
REM Command Prompt
cd vibecraft-framework
python install.py
```

Then restart your terminal or refresh PATH.

### Method 3: Local Install (Per-Project)

Installs vibecraft into your project directory — no admin rights required.

```bash
cd your-project
python vibecraft-framework\install-to-project.py
```

Then use:
```bash
vibecraft-local.bat --help
vibecraft-local.bat doctor
```

### Method 4: No Install (Python Launcher)

If you have Python installed, run directly:

```bash
py -m vibecraft --help
```

Or use the launcher:
```bash
vibecraft.bat --help
```

---

## PATH Refresh Options

After global installation, refresh your terminal session:

**Option 1: Restart terminal** (recommended)
- Close and reopen your terminal/PowerShell

**Option 2: PowerShell one-liner**
```powershell
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","User")
```

**Option 3: CMD refresh**
```cmd
setx PATH ""
```
Then close and reopen terminal.

---

## What the installer does

### Global Install (`install.py`, `install.bat`)

1. Installs the vibecraft Python package
2. Adds Python's `Scripts` directory to your PATH
3. Makes `vibecraft` command available globally

**Changes in v0.4:**
- Uses `setx` instead of registry editing (more reliable)
- Verifies PATH modification success
- Provides PATH refresh commands

### Local Install (`install-to-project.py`)

1. Creates `.vibecraft-venv/` in your project
2. Installs vibecraft into the virtual environment
3. Creates `vibecraft-local.bat` launcher

**Benefits:**
- No admin rights required
- Different versions per project
- Isolated dependencies

---

## After Installation

### 1. Verify installation

**Global install:**
```bash
vibecraft --help
vibecraft doctor
```

**Local install:**
```bash
vibecraft-local.bat --help
vibecraft-local.bat doctor
```

**No install (py launcher):**
```bash
py -m vibecraft --help
py -m vibecraft doctor
```

### 2. Start using vibecraft

```bash
# Create your research.md and stack.md files
# Then initialize a new project:
vibecraft init --research research.md --stack stack.md

# Check project status:
vibecraft status

# Run a skill:
vibecraft run research
```

---

## Troubleshooting

### "vibecraft is not recognized"

**For global install:**

1. Make sure you refreshed PATH after installation
2. Check if Scripts directory is in PATH:
   ```cmd
   echo %PATH%
   ```
3. Try running with py launcher:
   ```bash
   py -m vibecraft --help
   ```
4. Manually add to PATH:
   - Press Win+R, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Add Scripts path to user PATH

**For local install:**

1. Use the launcher: `vibecraft-local.bat --help`
2. Activate venv: `.vibecraft-venv\Scripts\activate`

### "Python not found"

Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/).

During installation, make sure to check "Add Python to PATH".

### Installation fails with PATH error

The installer can still install the package even if PATH modification fails.

**Manual steps:**
1. Run: `python install.py` (package will install)
2. Manually add Scripts to PATH (see above)
3. Or use: `py -m vibecraft`

### Local install fails

1. Ensure you have write permissions in the project directory
2. Check that Python 3.10+ is installed
3. Try: `python -m pip install --upgrade pip`

---

## Uninstall

### Global uninstall

```bash
# Uninstall the package
pip uninstall vibecraft

# (Optional) Remove Scripts directory from PATH manually
# Path: %LOCALAPPDATA%\Python\pythoncore-3.x-64\Scripts
```

### Local uninstall

```bash
# Delete the venv and launcher
rmdir /s .vibecraft-venv
del vibecraft-local.bat
```

---

## Installation Comparison

| Method | Admin Required | Per-Project | PATH Required | Best For |
|--------|---------------|-------------|---------------|----------|
| Global (`install.py`) | No | No | Yes | Single user, one version |
| Local (`install-to-project.py`) | No | Yes | No | Multiple projects, no admin |
| Py launcher (`py -m`) | No | No | No | Quick testing |
| Launcher (`vibecraft.bat`) | No | No | No | Development |

---
