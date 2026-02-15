@echo off
title Voiz - Installer
color 0A

echo.
echo  ============================================
echo    Voiz - Speech-to-Clipboard Installer
echo  ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ERROR] Python is not installed.
    echo.
    echo  Please install Python 3.10+ from:
    echo  https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Show Python version
echo  Found:
python --version
echo.

:: Install dependencies
echo  Installing dependencies...
echo  -------------------------------------------
python -m pip install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  [ERROR] Failed to install dependencies.
    echo  Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo  [OK] All dependencies installed successfully.
echo.

:: Ask about autostart
echo  -------------------------------------------
echo.
set /p AUTOSTART="  Start Voiz automatically with Windows? (y/n): "
if /i "%AUTOSTART%"=="y" (
    python "%~dp0autostart.py" --enable
    echo.
    echo  [OK] Autostart enabled.
) else (
    echo.
    echo  [OK] Autostart skipped. You can enable it later via the tray menu.
)

echo.
echo  ============================================
echo    Installation complete!
echo.
echo    Start Voiz by double-clicking: voiz.pyw
echo    Shortcut: Ctrl+Space to record
echo  ============================================
echo.
pause
