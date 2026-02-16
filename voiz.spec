# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Voiz - Speech-to-Clipboard & Text Tools.

Builds a single voiz.exe that runs without a console window.
All Python sources, dependencies, and the runtime are bundled.

Usage:
    pyinstaller voiz.spec
"""

import os
import sys

block_cipher = None

# Collect sounddevice portaudio binaries
import sounddevice
sounddevice_data = os.path.join(os.path.dirname(sounddevice.__file__), "_sounddevice_data")
sounddevice_datas = []
if os.path.isdir(sounddevice_data):
    for root, dirs, files in os.walk(sounddevice_data):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.relpath(root, os.path.dirname(sounddevice.__file__))
            sounddevice_datas.append((src, dst))


a = Analysis(
    ['voiz.pyw'],
    pathex=[],
    binaries=[],
    datas=sounddevice_datas,
    hiddenimports=[
        # pynput backends (Windows)
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'pynput._util.win32',
        # keyring backend
        'keyring.backends.Windows',
        # pystray backend
        'pystray._win32',
        # tkinter (for subprocess dialogs)
        'tkinter',
        'tkinter.simpledialog',
        'tkinter.messagebox',
        # sounddevice / soundfile
        'sounddevice',
        'soundfile',
        '_sounddevice_data',
        # standard lib used in subprocesses
        'ctypes',
        'ctypes.wintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='voiz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,             # No console window (like .pyw)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
