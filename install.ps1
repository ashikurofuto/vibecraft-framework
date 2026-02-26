# Vibecraft Installer for Windows (PowerShell)
#
# This script installs vibecraft and configures PATH automatically.
#
# Usage: .\install.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Vibecraft Installer (Windows)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing vibecraft..." -ForegroundColor Cyan
Write-Host ""

# Run the Python installer
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& python "$scriptDir\install.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Installation failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Please RESTART your terminal for changes to take effect." -ForegroundColor Yellow
Write-Host "After restarting, you can run 'vibecraft' from anywhere!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
