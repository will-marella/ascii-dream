"""
Entry point for ASCII Dream TUI application.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ascii_dream.tui_app import main as tui_main

if __name__ == "__main__":
    sys.exit(tui_main())
