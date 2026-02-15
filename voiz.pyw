"""Voiz Launcher -- double-click to start the app without a console window.

The .pyw extension causes Windows to use pythonw.exe,
which prevents a terminal window from appearing. The app runs
entirely in the background and is only visible via the system tray icon.
"""

import os
import sys

# Ensure imports from the app's own directory work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

main()
