# Voiz - Speech-to-Clipboard

Minimal Windows app that records your voice with **Ctrl+Space**, transcribes it using OpenAI Whisper, and copies the result to your clipboard.

## Features

- **Toggle recording**: Ctrl+Space to start, press again to stop
- **Automatic language detection**: Whisper detects the language automatically
- **Code-switching**: Correctly transcribes mixed languages (e.g. German with English terms)
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
| Change API key | Right-click tray icon → "Set API Key" |
| Toggle autostart | Right-click tray icon → "Start with Windows" |
| Quit the app | Right-click tray icon → "Quit" |

## Status Indicator (Tray Icon)

- **Green**: Ready to record
- **Red**: Recording in progress
- **Blue**: Transcription in progress

## Notes

- Ctrl+Space may conflict with some IDEs (e.g. VS Code autocomplete). The shortcut can be changed in `main.py`.
- The app also runs on macOS (API key is stored in the macOS Keychain instead).
