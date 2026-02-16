"""Voiz Launcher -- entry point for both normal and PyInstaller execution.

The .pyw extension causes Windows to use pythonw.exe (no console window).
When built with PyInstaller, this is the single entry point for everything:

  voiz.exe                  -> Start the main app
  voiz.exe --toolpicker     -> Show the tool picker popup (subprocess)
  voiz.exe --api-key-dialog -> Show the API key input dialog (subprocess)
  voiz.exe --error-dialog   -> Show an error message dialog (subprocess)
"""

import os
import sys

# Ensure imports from the app's own directory work correctly
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _run_toolpicker() -> None:
    from toolpicker import main as toolpicker_main
    toolpicker_main()


def _run_api_key_dialog() -> None:
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    key = simpledialog.askstring(
        "Voiz - API Key",
        "Please enter your OpenAI API key:\n\n"
        "Create a key at:\n"
        "https://platform.openai.com/api-keys",
        show="*",
        parent=root,
    )
    root.destroy()
    if key and key.strip():
        print(key.strip(), end="")


def _run_error_dialog() -> None:
    import tkinter as tk
    from tkinter import messagebox
    title = sys.argv[2] if len(sys.argv) > 2 else "Error"
    message = sys.argv[3] if len(sys.argv) > 3 else "An error occurred."
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showerror(title, message)
    root.destroy()


if __name__ == "__main__":
    if "--toolpicker" in sys.argv:
        _run_toolpicker()
    elif "--api-key-dialog" in sys.argv:
        _run_api_key_dialog()
    elif "--error-dialog" in sys.argv:
        _run_error_dialog()
    else:
        from main import main
        main()
