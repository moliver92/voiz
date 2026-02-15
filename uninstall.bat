@echo off
title Voiz - Uninstaller
color 0E

echo.
echo  ============================================
echo    Voiz - Uninstaller
echo  ============================================
echo.

:: Remove autostart entry
echo  Removing autostart entry...
python "%~dp0autostart.py" --disable 2>nul
echo  [OK] Autostart removed.
echo.

:: Remove stored API key
echo  Removing stored API key from Credential Manager...
python -c "from config import delete_api_key; delete_api_key()" 2>nul
echo  [OK] API key removed.
echo.

:: Uninstall pip packages
set /p UNINSTALL_DEPS="  Uninstall Python dependencies? (y/n): "
if /i "%UNINSTALL_DEPS%"=="y" (
    echo.
    echo  Uninstalling dependencies...
    echo  -------------------------------------------
    python -m pip uninstall -y -r "%~dp0requirements.txt" --quiet 2>nul
    echo.
    echo  [OK] Dependencies uninstalled.
) else (
    echo.
    echo  [OK] Dependencies kept.
)

echo.
echo  ============================================
echo    Voiz has been uninstalled.
echo.
echo    You can safely delete this folder now.
echo  ============================================
echo.
pause
