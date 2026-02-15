# Voiz - Speech-to-Clipboard & Text Tools

Minimal Windows app with two superpowers:

1. **Ctrl+Space** -- Record your voice, transcribe with OpenAI Whisper, copy to clipboard.
2. **Ctrl+Alt+Space** -- Open a tool palette to optimize or translate your clipboard text with GPT.

## Features

### Voice Recording
- **Toggle recording**: Ctrl+Space to start, press again to stop
- **Automatic language detection**: Whisper detects the language automatically
- **Code-switching**: Correctly transcribes mixed languages (e.g. German with English terms)

### Text Tools (Ctrl+Alt+Space)
- **Optimize for Email**: Formats clipboard text as a professional email with greeting, proper paragraphs, and closing
- **Optimize for Slack**: Rewrites clipboard text in a direct, casual chat-friendly style
- **Translate to English**: Translates clipboard text into English

### General
- **System tray**: Minimal tray icon with status indicator (green/red/blue)
- **Secure API key**: Stored in the Windows Credential Manager
- **Autostart**: Optionally start Voiz with Windows (toggle via tray menu)

## Prerequisites

- Python 3.10+
- A working microphone
- OpenAI API key ([create one here](https://platform.openai.com/api-keys))

## Installation

Double-click **`install.bat`**. It will:

1. Check that Python is installed
2. Install all dependencies
3. Optionally enable autostart with Windows

Alternatively, install manually:

```bash
cd voiz
pip install -r requirements.txt
```

### Uninstall

Double-click **`uninstall.bat`**. It removes the autostart entry, deletes the stored API key from the Credential Manager, and optionally uninstalls the Python dependencies.

## Getting Started

### Double-click (recommended)

Simply double-click **`voiz.pyw`**. The app starts in the background without a console window and appears only as a tray icon next to the clock.

### Via terminal

```bash
python main.py
```

On first launch, a dialog will ask for your OpenAI API key. It is securely stored in the Windows Credential Manager.

## Usage

| Action | Shortcut / Menu |
|---|---|
| Start recording | Ctrl+Space |
| Stop recording | Ctrl+Space (again) |
| Open text tools | Ctrl+Alt+Space |
| Change API key | Right-click tray icon → "Set API Key" |
| Toggle autostart | Right-click tray icon → "Start with Windows" |
| Quit the app | Right-click tray icon → "Quit" |

## Status Indicator (Tray Icon)

- **Green**: Ready
- **Red**: Recording in progress
- **Blue**: Processing (transcription or text optimization)

## Notes

- Ctrl+Space may conflict with some IDEs (e.g. VS Code autocomplete). Shortcuts can be changed in `main.py`.
- The app also runs on macOS (API key is stored in the macOS Keychain instead).
