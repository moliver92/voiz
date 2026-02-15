"""API key management with keyring (Windows Credential Manager / macOS Keychain).

All GUI dialogs run in separate subprocesses to avoid threading conflicts
with pystray (Tcl_AsyncDelete crash).
"""

import subprocess
import sys
import textwrap

import keyring

SERVICE_NAME = "voiz-speech-to-clipboard"
KEY_NAME = "openai_api_key"


def _python_exe() -> str:
    """Returns the path to the current python(w) executable.

    Ensures the subprocess works correctly with both python.exe and pythonw.exe.
    """
    return sys.executable


def get_api_key() -> str | None:
    """Reads the stored OpenAI API key from the Credential Manager."""
    return keyring.get_password(SERVICE_NAME, KEY_NAME)


def set_api_key(api_key: str) -> None:
    """Stores the OpenAI API key in the Credential Manager."""
    keyring.set_password(SERVICE_NAME, KEY_NAME, api_key)


def delete_api_key() -> None:
    """Deletes the stored API key."""
    try:
        keyring.delete_password(SERVICE_NAME, KEY_NAME)
    except keyring.errors.PasswordDeleteError:
        pass


def _show_error_gui(title: str, message: str) -> None:
    """Shows an error message as a GUI dialog in a subprocess."""
    script = textwrap.dedent(f"""\
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror({title!r}, {message!r})
        root.destroy()
    """)
    try:
        subprocess.run(
            [_python_exe(), "-c", script],
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
            if sys.platform == "win32" else 0,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass


def prompt_api_key_gui() -> str | None:
    """Shows a tkinter input dialog in a separate process.

    Returns:
        The entered API key, or None if cancelled.
    """
    script = textwrap.dedent("""\
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        key = simpledialog.askstring(
            "Voiz - API Key",
            "Please enter your OpenAI API key:\\n\\n"
            "Create a key at:\\n"
            "https://platform.openai.com/api-keys",
            show="*",
            parent=root,
        )
        root.destroy()
        if key and key.strip():
            print(key.strip(), end="")
    """)

    try:
        result = subprocess.run(
            [_python_exe(), "-c", script],
            capture_output=True,
            text=True,
            timeout=120,
            creationflags=subprocess.CREATE_NO_WINDOW
            if sys.platform == "win32" else 0,
        )
        if result.returncode == 0 and result.stdout.strip():
            api_key = result.stdout.strip()
            set_api_key(api_key)
            return api_key
    except (subprocess.TimeoutExpired, OSError):
        pass

    return None


def ensure_api_key() -> str:
    """Ensures an API key is available, prompting the user if necessary.

    Returns:
        The API key.

    Raises:
        SystemExit: If no key is provided.
    """
    api_key = get_api_key()
    if api_key:
        return api_key

    # GUI dialog for API key input
    api_key = prompt_api_key_gui()
    if not api_key:
        _show_error_gui(
            "Voiz - Error",
            "Voiz cannot function without an API key.\nThe app will now exit.",
        )
        raise SystemExit(1)

    return api_key
