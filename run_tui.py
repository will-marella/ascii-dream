#!/usr/bin/env python3
"""
Run the ASCII Dream TUI with Modal backend.

Usage: modal run run_tui.py
"""
from ascii_dream.tui import tui_main, modal_app

# Re-export the modal app for modal run to find it
app = modal_app

if __name__ == "__main__":
    tui_main()
