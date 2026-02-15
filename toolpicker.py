"""Tool picker popup -- runs as a subprocess to avoid tkinter/pystray conflicts.

Shows a small always-on-top window with tool options.
Prints the selected mode to stdout and exits.

Usage (as subprocess):
    result = subprocess.run([sys.executable, "toolpicker.py"], capture_output=True, text=True)
    mode = result.stdout.strip()  # "email", "slack", "translate", or ""
"""

import tkinter as tk
import sys


def main() -> None:
    root = tk.Tk()
    root.title("Voiz Tools")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    # Remove window decorations for a cleaner look, keep close button feel
    root.overrideredirect(True)

    selected = {"mode": ""}

    def select(mode: str) -> None:
        selected["mode"] = mode
        root.destroy()

    def on_escape(_event: object = None) -> None:
        root.destroy()

    root.bind("<Escape>", on_escape)
    # Also close if window loses focus
    root.bind("<FocusOut>", lambda _: root.after(100, _check_focus))

    def _check_focus() -> None:
        try:
            if not root.focus_get():
                root.destroy()
        except tk.TclError:
            pass

    # --- Styling ---
    bg = "#1e1e2e"
    fg = "#cdd6f4"
    accent_email = "#89b4fa"
    accent_slack = "#a6e3a1"
    accent_translate = "#f9e2af"
    hover_bg = "#313244"
    font_title = ("Segoe UI", 11, "bold")
    font_btn = ("Segoe UI", 10)
    font_shortcut = ("Segoe UI", 8)

    root.configure(bg=bg)

    # Title bar
    title_frame = tk.Frame(root, bg=bg, padx=16, pady=10)
    title_frame.pack(fill="x")

    tk.Label(
        title_frame, text="Voiz Tools", font=font_title,
        bg=bg, fg=fg,
    ).pack(side="left")

    tk.Label(
        title_frame, text="ESC to close", font=font_shortcut,
        bg=bg, fg="#6c7086",
    ).pack(side="right")

    # Separator
    tk.Frame(root, bg="#313244", height=1).pack(fill="x", padx=12)

    # Button container
    btn_frame = tk.Frame(root, bg=bg, padx=12, pady=8)
    btn_frame.pack(fill="x")

    accent_translate_de = "#cba6f7"

    buttons = [
        ("email", "\u2709  Optimize for Email", accent_email,
         "Formal, polite, proper paragraphs"),
        ("slack", "\u26a1  Optimize for Slack", accent_slack,
         "Direct, casual, chat-friendly"),
        ("translate_en", "\U0001f310  Translate to English", accent_translate,
         "Translate clipboard text to English"),
        ("translate_de", "\U0001f1e9\U0001f1ea  Translate to German", accent_translate_de,
         "Translate clipboard text to German"),
    ]

    for mode, label, accent, description in buttons:
        frame = tk.Frame(btn_frame, bg=bg, cursor="hand2")
        frame.pack(fill="x", pady=3)

        # Accent bar on the left
        tk.Frame(frame, bg=accent, width=3).pack(side="left", fill="y", padx=(0, 10))

        text_frame = tk.Frame(frame, bg=bg)
        text_frame.pack(side="left", fill="x", expand=True, pady=6)

        tk.Label(
            text_frame, text=label, font=font_btn,
            bg=bg, fg=fg, anchor="w",
        ).pack(fill="x")

        tk.Label(
            text_frame, text=description, font=font_shortcut,
            bg=bg, fg="#6c7086", anchor="w",
        ).pack(fill="x")

        # Make entire row clickable
        def _bind_click(widget: tk.Widget, m: str = mode) -> None:
            widget.bind("<Button-1>", lambda _: select(m))
            for child in widget.winfo_children():
                _bind_click(child, m)

        def _bind_hover(widget: tk.Widget, f: tk.Frame = frame) -> None:
            widget.bind("<Enter>", lambda _: _set_bg(f, hover_bg))
            widget.bind("<Leave>", lambda _: _set_bg(f, bg))

        def _set_bg(widget: tk.Widget, color: str) -> None:
            try:
                widget.configure(bg=color)
                for child in widget.winfo_children():
                    _set_bg(child, color)
            except tk.TclError:
                pass

        _bind_click(frame)
        _bind_hover(frame)

    # Bottom padding
    tk.Frame(root, bg=bg, height=6).pack()

    # --- Center on screen ---
    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    # Rounded corners effect (Windows 11)
    try:
        from ctypes import windll, c_int, byref, sizeof
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWM_ROUND = c_int(2)
        hwnd = windll.user32.GetParent(root.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, byref(DWM_ROUND), sizeof(DWM_ROUND),
        )
    except Exception:
        pass

    root.focus_force()
    root.mainloop()

    # Output the selected mode
    if selected["mode"]:
        print(selected["mode"], end="")


if __name__ == "__main__":
    main()
