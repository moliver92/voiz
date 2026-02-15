"""Voiz - Speech-to-Clipboard.

Minimal app: press Ctrl+Space, speak, press again,
transcription lands in your clipboard.
"""

import ctypes
import sys
import threading


# ---------------------------------------------------------------------------
# Windows: Set app name in notifications to "Voiz"
# ---------------------------------------------------------------------------

def _set_app_id() -> None:
    """Sets the Windows AppUserModelID so that notifications
    display 'Voiz' instead of 'Python' as the app name."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Voiz")
        except Exception:
            pass


_set_app_id()

import pyperclip
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard
import pystray

from config import ensure_api_key, prompt_api_key_gui
from recorder import Recorder
from transcriber import transcribe


# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------

class AppState:
    """Central application state."""

    IDLE = "idle"           # Green - ready
    RECORDING = "recording" # Red   - recording
    PROCESSING = "processing"  # Blue - transcribing

    def __init__(self) -> None:
        self.status = self.IDLE
        self.recorder = Recorder()
        self.api_key: str = ""
        self.tray: pystray.Icon | None = None
        self._lock = threading.Lock()
        self._toggle_lock = threading.Lock()  # Guards toggle_recording

    def set_status(self, status: str) -> None:
        with self._lock:
            self.status = status
        self._update_icon()

    def _update_icon(self) -> None:
        if self.tray:
            self.tray.icon = create_icon(self.status)


# ---------------------------------------------------------------------------
# Icon Generation
# ---------------------------------------------------------------------------

ICON_SIZE = 64
RENDER_SCALE = 4  # Draw at 4x, then downscale for anti-aliasing

COLOR_MAP = {
    AppState.IDLE: "#22c55e",        # Green
    AppState.RECORDING: "#ef4444",   # Red
    AppState.PROCESSING: "#3b82f6",  # Blue
}


def create_icon(status: str) -> Image.Image:
    """Creates a tray icon with a microphone silhouette.

    Drawn at 4x resolution and downscaled for smooth edges.
    """
    color = COLOR_MAP.get(status, "#22c55e")
    S = ICON_SIZE * RENDER_SCALE  # 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = S // 16  # 16px padding at 256

    # --- Background: rounded square ---
    radius = S // 5
    draw.rounded_rectangle([pad, pad, S - pad, S - pad], radius=radius, fill=color)

    # --- Microphone silhouette (white) ---
    white = "#ffffff"
    cx = S // 2  # Center X

    # Microphone head (capsule: rounded rectangle)
    mic_w = S // 5          # Microphone width
    mic_top = S * 22 // 100
    mic_bot = S * 52 // 100
    mic_radius = mic_w // 2
    draw.rounded_rectangle(
        [cx - mic_w, mic_top, cx + mic_w, mic_bot],
        radius=mic_radius,
        fill=white,
    )

    # Holder (U-shaped arc below the microphone)
    arc_margin = S * 8 // 100
    arc_top = S * 38 // 100
    arc_bot = S * 65 // 100
    arc_width = S // 18
    draw.arc(
        [cx - mic_w - arc_margin, arc_top, cx + mic_w + arc_margin, arc_bot],
        start=0, end=180,
        fill=white, width=arc_width,
    )

    # Stem (vertical line below the arc)
    stem_top = S * 58 // 100
    stem_bot = S * 72 // 100
    stem_w = arc_width // 2
    draw.rectangle(
        [cx - stem_w, stem_top, cx + stem_w, stem_bot],
        fill=white,
    )

    # Base (horizontal line)
    foot_w = S * 12 // 100
    foot_y = stem_bot
    foot_h = arc_width // 2
    draw.rounded_rectangle(
        [cx - foot_w, foot_y, cx + foot_w, foot_y + foot_h],
        radius=foot_h // 2,
        fill=white,
    )

    # --- Downscale for smooth anti-aliasing ---
    img = img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    return img


# ---------------------------------------------------------------------------
# Desktop Notifications
# ---------------------------------------------------------------------------

def notify(tray: pystray.Icon, title: str, message: str) -> None:
    """Shows a desktop notification via the tray icon."""
    try:
        tray.notify(message, title)
    except Exception:
        # Silently ignore if notification fails
        pass


# ---------------------------------------------------------------------------
# Recording Toggle (Core Logic)
# ---------------------------------------------------------------------------

MIN_AUDIO_SIZE = 5000  # Minimum size in bytes (~0.15s at 16kHz mono)


def toggle_recording(state: AppState) -> None:
    """Starts or stops recording and processes the result."""

    # Lock prevents race conditions on rapid double-presses
    if not state._toggle_lock.acquire(blocking=False):
        return
    try:
        _toggle_recording_inner(state)
    finally:
        state._toggle_lock.release()


def _toggle_recording_inner(state: AppState) -> None:
    """Internal toggle logic (guarded by _toggle_lock)."""

    if state.status == AppState.PROCESSING:
        # Do nothing while processing
        return

    if state.status == AppState.IDLE:
        # --- Start recording ---
        try:
            state.recorder.start()
            state.set_status(AppState.RECORDING)
            if state.tray:
                notify(state.tray, "Voiz", "Recording started...")
        except Exception as e:
            if state.tray:
                notify(state.tray, "Voiz - Error", f"Microphone error: {e}")
            state.set_status(AppState.IDLE)
        return

    if state.status == AppState.RECORDING:
        # --- Stop recording + transcribe ---
        audio_bytes = state.recorder.stop()

        if not audio_bytes or len(audio_bytes) < MIN_AUDIO_SIZE:
            if state.tray:
                notify(state.tray, "Voiz", "Recording too short. Please speak longer.")
            state.set_status(AppState.IDLE)
            return

        state.set_status(AppState.PROCESSING)

        # Run transcription in a separate thread to avoid blocking the UI
        def _process() -> None:
            try:
                text = transcribe(audio_bytes, state.api_key)
                if text:
                    pyperclip.copy(text)
                    if state.tray:
                        # Preview: first 80 characters
                        preview = text[:80] + ("..." if len(text) > 80 else "")
                        notify(state.tray, "Voiz - Copied!", preview)
                else:
                    if state.tray:
                        notify(state.tray, "Voiz", "No speech detected.")
            except Exception as e:
                err_msg = str(e)
                if "auth" in err_msg.lower() or "api key" in err_msg.lower():
                    err_msg = "Invalid API key. Please update it via the tray menu."
                if state.tray:
                    notify(state.tray, "Voiz - Error", err_msg)
            finally:
                state.set_status(AppState.IDLE)

        threading.Thread(target=_process, daemon=True).start()


# ---------------------------------------------------------------------------
# Hotkey Listener
# ---------------------------------------------------------------------------

def setup_hotkey_listener(state: AppState) -> keyboard.GlobalHotKeys:
    """Sets up the global Ctrl+Space hotkey."""

    hotkey = keyboard.GlobalHotKeys({
        "<ctrl>+<space>": lambda: toggle_recording(state),
    })
    hotkey.daemon = True
    hotkey.start()
    return hotkey


# ---------------------------------------------------------------------------
# System Tray
# ---------------------------------------------------------------------------

def on_set_api_key(state: AppState) -> None:
    """Context menu action: change API key."""
    new_key = prompt_api_key_gui()
    if new_key:
        state.api_key = new_key


def on_quit(state: AppState, icon: pystray.Icon) -> None:
    """Context menu action: quit the app."""
    icon.stop()


def create_tray(state: AppState) -> pystray.Icon:
    """Creates the system tray icon with context menu."""
    menu = pystray.Menu(
        pystray.MenuItem(
            "Set API Key",
            lambda icon, item: on_set_api_key(state),
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "Quit",
            lambda icon, item: on_quit(state, icon),
        ),
    )

    icon = pystray.Icon(
        name="voiz",
        icon=create_icon(AppState.IDLE),
        title="Voiz - Speech-to-Clipboard (Ctrl+Space)",
        menu=menu,
    )

    return icon


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point."""

    # Ensure API key is available
    api_key = ensure_api_key()

    # Initialize app state
    state = AppState()
    state.api_key = api_key

    # Start hotkey listener
    hotkey_listener = setup_hotkey_listener(state)

    # Create and run system tray (blocks)
    tray = create_tray(state)
    state.tray = tray

    try:
        tray.run()
    except KeyboardInterrupt:
        pass
    finally:
        hotkey_listener.stop()
        if state.recorder.is_recording:
            state.recorder.stop()


if __name__ == "__main__":
    main()
