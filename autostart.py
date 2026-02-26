"""Manage autostart for Voiz (Windows and macOS).

Windows:
    Creates/removes a VBScript launcher in the Windows Startup folder.
    A .vbs file is used instead of a shortcut to launch pythonw.exe silently
    without any flickering console window.

macOS:
    Creates/removes a LaunchAgent plist in ~/Library/LaunchAgents/.
    The plist runs `python main.py` (or the frozen .app) at login.

Can be used as a module (from main.py) or as a CLI:
    python autostart.py --enable
    python autostart.py --disable
    python autostart.py --status
"""

import os
import sys

APP_NAME = "Voiz"
MACOS_PLIST_LABEL = "com.voiz.app"
_FROZEN = getattr(sys, 'frozen', False)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _entry_point() -> str:
    """Returns the absolute path to the Voiz entry point.

    In PyInstaller/frozen mode, this is the executable itself.
    In development mode on Windows, this is voiz.pyw.
    In development mode on macOS/Linux, this is main.py.
    """
    if _FROZEN:
        return sys.executable
    base = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == "win32":
        return os.path.join(base, "voiz.pyw")
    return os.path.join(base, "main.py")


# ---------------------------------------------------------------------------
# Windows implementation
# ---------------------------------------------------------------------------

def _win_startup_folder() -> str:
    return os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )


def _win_startup_file() -> str:
    return os.path.join(_win_startup_folder(), f"{APP_NAME}.vbs")


def _win_pythonw() -> str:
    if _FROZEN:
        return ""
    exe = sys.executable
    pythonw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.isfile(pythonw):
        return pythonw
    if exe.lower().endswith("pythonw.exe"):
        return exe
    return exe


def _win_is_enabled() -> bool:
    return os.path.isfile(_win_startup_file())


def _win_enable() -> bool:
    try:
        voiz_path = _entry_point()
        q = '"'
        if _FROZEN:
            vbs_content = (
                f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run {q}{q}{q}{voiz_path}{q}{q}{q}, 0, False\n'
            )
        else:
            pythonw = _win_pythonw()
            vbs_content = (
                f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run {q}{q}{q}{pythonw}{q}{q} {q}{q}{voiz_path}{q}{q}{q}, 0, False\n'
            )
        startup_file = _win_startup_file()
        os.makedirs(os.path.dirname(startup_file), exist_ok=True)
        with open(startup_file, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        return True
    except OSError:
        return False


def _win_disable() -> bool:
    try:
        f = _win_startup_file()
        if os.path.isfile(f):
            os.remove(f)
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# macOS implementation
# ---------------------------------------------------------------------------

def _mac_plist_path() -> str:
    return os.path.join(
        os.path.expanduser("~"), "Library", "LaunchAgents",
        f"{MACOS_PLIST_LABEL}.plist",
    )


def _mac_plist_content() -> str:
    entry = _entry_point()
    if _FROZEN:
        program_args = f"        <string>{entry}</string>"
    else:
        program_args = (
            f"        <string>{sys.executable}</string>\n"
            f"        <string>{entry}</string>"
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{MACOS_PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
{program_args}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/voiz.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/voiz.err</string>
</dict>
</plist>
"""


def _mac_is_enabled() -> bool:
    return os.path.isfile(_mac_plist_path())


def _mac_enable() -> bool:
    try:
        plist_path = _mac_plist_path()
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(_mac_plist_content())
        # Register with launchd so it takes effect immediately (without reboot)
        os.system(f'launchctl load "{plist_path}" 2>/dev/null')
        return True
    except OSError:
        return False


def _mac_disable() -> bool:
    try:
        plist_path = _mac_plist_path()
        if os.path.isfile(plist_path):
            os.system(f'launchctl unload "{plist_path}" 2>/dev/null')
            os.remove(plist_path)
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Public API (platform-agnostic)
# ---------------------------------------------------------------------------

def _startup_file() -> str:
    """Returns the autostart file path for the current platform."""
    if sys.platform == "darwin":
        return _mac_plist_path()
    return _win_startup_file()


def is_enabled() -> bool:
    """Checks if Voiz autostart is enabled."""
    if sys.platform == "darwin":
        return _mac_is_enabled()
    return _win_is_enabled()


def enable() -> bool:
    """Enables autostart for the current platform.

    Returns:
        True if successful, False otherwise.
    """
    if sys.platform == "darwin":
        return _mac_enable()
    return _win_enable()


def disable() -> bool:
    """Disables autostart for the current platform.

    Returns:
        True if successful, False otherwise.
    """
    if sys.platform == "darwin":
        return _mac_disable()
    return _win_disable()


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
# CLI interface (used by install.bat / manual setup)
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
