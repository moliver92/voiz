"""Manage Windows autostart for Voiz.

Creates/removes a VBScript launcher in the Windows Startup folder.
A .vbs file is used instead of a shortcut to launch pythonw.exe silently
without any flickering console window.

Can be used as a module (from main.py) or as a CLI:
    python autostart.py --enable
    python autostart.py --disable
    python autostart.py --status
"""

import os
import sys
import textwrap

APP_NAME = "Voiz"
_FROZEN = getattr(sys, 'frozen', False)


def _startup_folder() -> str:
    """Returns the path to the Windows Startup folder."""
    return os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )


def _startup_file() -> str:
    """Returns the full path to the Voiz autostart .vbs file."""
    return os.path.join(_startup_folder(), f"{APP_NAME}.vbs")


def _voiz_pyw_path() -> str:
    """Returns the absolute path to the Voiz entry point.

    In PyInstaller mode, this is the .exe itself.
    In development mode, this is voiz.pyw.
    """
    if _FROZEN:
        return sys.executable
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "voiz.pyw")


def _pythonw_path() -> str:
    """Returns the path to pythonw.exe (no-console Python).

    In PyInstaller mode, returns None (the .exe IS the launcher).
    Falls back to the current executable if pythonw is not found.
    """
    if _FROZEN:
        return ""
    exe = sys.executable
    directory = os.path.dirname(exe)
    pythonw = os.path.join(directory, "pythonw.exe")
    if os.path.isfile(pythonw):
        return pythonw
    # If already running as pythonw.exe
    if exe.lower().endswith("pythonw.exe"):
        return exe
    return exe


def is_enabled() -> bool:
    """Checks if Voiz autostart is enabled."""
    return os.path.isfile(_startup_file())


def enable() -> bool:
    """Enables autostart by creating a .vbs launcher in the Startup folder.

    Returns:
        True if successful, False otherwise.
    """
    try:
        voiz_path = _voiz_pyw_path()

        q = '"'
        if _FROZEN:
            # PyInstaller .exe: just run the exe directly
            vbs_content = (
                f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run {q}{q}{q}{voiz_path}{q}{q}{q}, 0, False\n'
            )
        else:
            # Development mode: run pythonw.exe with voiz.pyw
            pythonw = _pythonw_path()
            vbs_content = (
                f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run {q}{q}{q}{pythonw}{q}{q} {q}{q}{voiz_path}{q}{q}{q}, 0, False\n'
            )

        startup_file = _startup_file()
        os.makedirs(os.path.dirname(startup_file), exist_ok=True)

        with open(startup_file, "w", encoding="utf-8") as f:
            f.write(vbs_content)

        return True
    except OSError:
        return False


def disable() -> bool:
    """Disables autostart by removing the .vbs launcher from the Startup folder.

    Returns:
        True if successful, False otherwise.
    """
    try:
        startup_file = _startup_file()
        if os.path.isfile(startup_file):
            os.remove(startup_file)
        return True
    except OSError:
        return False


def toggle() -> bool:
    """Toggles autostart on/off.

    Returns:
        True if autostart is now enabled, False if disabled.
    """
    if is_enabled():
        disable()
        return False
    else:
        enable()
        return True


# ---------------------------------------------------------------------------
# CLI interface (used by install.bat)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--enable" in sys.argv:
        if enable():
            print(f"  Autostart enabled: {_startup_file()}")
        else:
            print("  Failed to enable autostart.", file=sys.stderr)
            sys.exit(1)
    elif "--disable" in sys.argv:
        if disable():
            print("  Autostart disabled.")
        else:
            print("  Failed to disable autostart.", file=sys.stderr)
            sys.exit(1)
    elif "--status" in sys.argv:
        print(f"  Autostart: {'enabled' if is_enabled() else 'disabled'}")
    else:
        print("Usage: python autostart.py [--enable | --disable | --status]")
