#!/usr/bin/env python3
"""
Test the TUI display with a sample image (without Modal backend).
"""
from PIL import Image
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.binding import Binding
from rich.text import Text
from ascii_dream.rendering.ascii_converter import AsciiConverter


class TestDisplayScreen(Screen):
    """Test screen to display ASCII art."""

    CSS = """
    TestDisplayScreen {
        background: #000000;
    }

    #ascii-display {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: #ffffff;
    }

    #status-bar {
        dock: bottom;
        width: 100%;
        height: 3;
        background: #141414;
        color: #666666;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "quit", "Quit", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the test screen."""
        yield Static("Loading...", id="ascii-display")
        yield Static("Loading test image...", id="status-bar")

    def on_mount(self) -> None:
        """Load and display the test image."""
        # Load test image
        image = Image.open("ascii_dream/practice-images/image.webp")

        # Convert to ASCII
        converter = AsciiConverter(width=None)
        ascii_art = converter.convert(image)

        # Create Text object from ANSI art
        text_art = Text.from_ansi(ascii_art.rstrip())
        text_art.append("\n\n")
        text_art.append("Test Image - Loaded from image.webp", style="dim italic")

        # Update display
        self.query_one("#ascii-display").update(text_art)
        self.query_one("#status-bar").update("Press Q to quit")

    def action_quit(self) -> None:
        """Quit the app."""
        self.app.exit()


class TestApp(App):
    """Test TUI application."""

    def on_mount(self) -> None:
        """Show test screen."""
        self.push_screen(TestDisplayScreen())


if __name__ == "__main__":
    app = TestApp()
    app.run()
