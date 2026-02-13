#!/usr/bin/env python3
"""
ASCII Dream - Beautiful TUI application with Textual + Modal backend.
"""
import sys
import io
import asyncio
import threading
import queue
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Static
from textual.screen import Screen
from textual import work
from textual.binding import Binding


from PIL import Image
from rich.text import Text

# Import Modal backend and generation components
from .modal_backend import app as modal_app, get_generator
from .prompt_evolution import get_evolver
from .ascii_converter import AsciiConverter

# Define config constants
IMAGE_SIZE = 256  # 1:1 aspect ratio, fast mode
FPS = 1.0
JOURNEY_THEME = "abstract"
ASCII_WIDTH = 80


# ASCII art title for ASCII DREAM
ASCII_TITLE = """ █████╗ ███████╗ ██████╗██╗██╗    ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗
██╔══██╗██╔════╝██╔════╝██║██║    ██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║
███████║███████╗██║     ██║██║    ██║  ██║██████╔╝█████╗  ███████║██╔████╔██║
██╔══██║╚════██║██║     ██║██║    ██║  ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║
██║  ██║███████║╚██████╗██║██║    ██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"""


class MainMenuScreen(Screen):
    """Main menu screen - simplified."""

    CSS = """
    MainMenuScreen {
        align: center middle;
        background: $background;
    }

    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
    }

    #tagline {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
        margin-bottom: 2;
    }

    #controls {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $warning;
        margin-top: 2;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("escape", "quit", "Quit", show=False),
        Binding("enter", "start_dream", "Start", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the main menu."""
        yield Static(ASCII_TITLE, id="title")
        yield Static("Generate beautiful, evolving ASCII art from AI dreams", id="tagline")
        yield Static("Press Enter to Dream  •  Q/Esc to Quit", id="controls")

    def action_start_dream(self) -> None:
        """Start the dream generation."""
        self.app.push_screen(LoadingScreen())


class LoadingScreen(Screen):
    """Loading screen while initial frame is being generated."""

    CSS = """
    LoadingScreen {
        align: center middle;
        background: $background;
    }

    #loading-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 2 4;
        background: $surface;
    }

    .loading-row {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 1;
    }

    #timer {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        margin-top: 1;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "app.quit", "Quit", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.start_time = None

    def compose(self) -> ComposeResult:
        """Compose loading screen."""
        with Center():
            with Container(id="loading-box"):
                yield Static("[bold cyan]Loading Dream...[/bold cyan]", classes="loading-row")
                yield Static("", classes="loading-row")
                yield Static("0s", id="timer")
                yield Static("", classes="loading-row")
                yield Static("Should take approximately 60s", classes="loading-row")

    def on_mount(self) -> None:
        """Start generation when mounted."""
        import time
        self.start_time = time.time()
        self.set_interval(0.1, self.update_timer)
        
        # Start continuous generation in background
        self.app.start_continuous_generation()
        
        # Wait for first frame
        self.wait_for_first_frame()

    def update_timer(self) -> None:
        """Update elapsed time display."""
        if self.start_time is None:
            return
        try:
            import time
            elapsed = int(time.time() - self.start_time)
            timer = self.query_one("#timer", Static)
            timer.update(f"{elapsed}s")
        except Exception:
            pass

    @work(exclusive=True, thread=True)
    def wait_for_first_frame(self) -> None:
        """Wait for first frame to be generated, then transition to playback."""
        try:
            # Block until first frame is ready (with generous timeout)
            first_frame = self.app.get_next_frame(timeout=120)
            
            if first_frame:
                # Transition to playback screen on main thread
                self.app.call_from_thread(self._start_playback, first_frame)
            else:
                self.app.call_from_thread(self.dismiss)
                self.app.call_from_thread(self.app.notify, "No frames generated", "error")
        except Exception as e:
            self.app.call_from_thread(self.dismiss)
            self.app.call_from_thread(self.app.notify, f"Error: {e}", "error")
    
    def _start_playback(self, first_frame):
        """Start playback screen (called from main thread)."""
        self.app.pop_screen()
        self.app.push_screen(DreamGenerationScreen(first_frame=first_frame))


class DreamGenerationScreen(Screen):
    """The actual dream generation and display screen with continuous generation."""

    CSS = """
    DreamGenerationScreen {
        align: center middle;
        background: #000000;
    }

    #ascii-display {
        width: 100%;
        height: auto;
        content-align: center middle;
        background: #000000;
    }

    #status {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        dock: bottom;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "stop_and_back", "Back", show=False, priority=True),
        Binding("q", "stop_and_quit", "Quit", show=False),
        Binding("space", "pause_resume", "Pause/Resume", show=False),
    ]

    def __init__(self, first_frame: tuple):
        super().__init__()
        self.current_frame = first_frame  # (ascii_art, prompt)
        self.is_paused = False

    def compose(self) -> ComposeResult:
        """Compose the generation screen."""
        yield Static("", id="ascii-display")
        yield Static("Esc: Back  •  Q: Quit  •  Space: Pause/Resume", id="status")

    def on_mount(self) -> None:
        """Start playback when screen mounts."""
        # Show first frame immediately
        self._display_frame(self.current_frame)
        
        # Start pulling frames from queue at FPS rate
        fps = FPS
        interval = 1.0 / fps
        self.set_interval(interval, self._get_and_display_next_frame)

    def _display_frame(self, frame: tuple) -> None:
        """Display a frame on screen."""
        ascii_art, prompt = frame
        
        try:
            display = self.query_one("#ascii-display", Static)
            # Use Text.from_ansi to properly handle ANSI codes in ASCII art
            art_text = Text.from_ansi(ascii_art)
            # Add prompt as a separate line using Text (not f-string to avoid markup issues)
            art_text.append("\n\n")
            art_text.append(prompt, style="dim italic")
            display.update(art_text)
        except Exception:
            pass

    def _get_and_display_next_frame(self) -> None:
        """Pull next frame from queue and display it."""
        if self.is_paused:
            return
        
        # Try to get next frame from queue (non-blocking)
        frame = self.app.get_next_frame(timeout=0.01)
        if frame:
            self.current_frame = frame
            self._display_frame(frame)
        # If no frame available, just keep showing current frame

    def action_pause_resume(self) -> None:
        """Toggle pause/resume."""
        self.is_paused = not self.is_paused
        try:
            status = self.query_one("#status", Static)
            if self.is_paused:
                status.update("[yellow]PAUSED[/yellow]  •  Space: Resume  •  Esc: Back  •  Q: Quit")
            else:
                status.update("Esc: Back  •  Q: Quit  •  Space: Pause/Resume")
        except Exception:
            pass

    def on_unmount(self) -> None:
        """Clean up when screen is closed."""
        # Stop the background generation thread
        self.app.stop_continuous_generation()

    def action_stop_and_back(self) -> None:
        """Stop and go back."""
        self.dismiss()

    def action_stop_and_quit(self) -> None:
        """Stop and quit app."""
        self.app.exit()


class ASCIIDreamApp(App):
    """ASCII Dream TUI application."""

    CSS = """
    Screen {
        background: $background;
    }
    """

    COLORS = {
        "background": "#000000",
        "surface": "#141414",
        "primary": "#00ffff",
        "accent": "#00ffff",
        "success": "#00ff00",
        "warning": "#ffff00",
        "error": "#ff0000",
        "text": "#ffffff",
        "text-muted": "#666666",
    }

    def __init__(self, generator=None):
        super().__init__()
        self.generator = generator  # Modal generator passed from entrypoint
        self.prompt_iterator = None
        self.converter = None
        self.frame_queue = None
        self.generator_thread = None
        self.stop_generation = None

    def on_mount(self) -> None:
        """Initialize the app."""
        self.push_screen(MainMenuScreen())

    def _initialize_generation(self):
        """Initialize the prompt iterator and converter."""
        
        # Initialize converter
        self.converter = AsciiConverter(width=ASCII_WIDTH)
        self.image_width = IMAGE_SIZE
        self.image_height = IMAGE_SIZE
        
        # Get prompts - infinite iterator
        self.prompt_iterator = get_evolver(
            journey=JOURNEY_THEME,
            start_prompt=None,
            custom=False,
        )

    def start_continuous_generation(self, queue_depth: int = 3):
        """Start background thread for continuous frame generation."""
        if self.generator is None:
            return
        
        # Initialize if not already done
        if self.prompt_iterator is None:
            self._initialize_generation()
        
        # Create queue and stop event
        self.frame_queue = queue.Queue(maxsize=queue_depth)
        self.stop_generation = threading.Event()
        
        # Start producer thread
        self.generator_thread = threading.Thread(
            target=self._generation_worker,
            daemon=True
        )
        self.generator_thread.start()

    def _generation_worker(self):
        """Background worker that continuously generates frames."""
        while not self.stop_generation.is_set():
            try:
                # Get next prompt
                prompt = next(self.prompt_iterator)
                
                # Generate image via Modal (blocking call)
                image_bytes = self.generator.generate.remote(
                    prompt, height=self.image_height, width=self.image_width, seed=None
                )
                
                # Convert to ASCII
                image = Image.open(io.BytesIO(image_bytes))
                ascii_art = self.converter.convert(image)
                
                # Put in queue (blocks if queue is full - natural backpressure)
                self.frame_queue.put((ascii_art, prompt))
                
            except Exception as e:
                # On error, put error frame
                try:
                    self.frame_queue.put((f"[Error: {e}]", "error"), timeout=1)
                except queue.Full:
                    pass

    def stop_continuous_generation(self):
        """Stop the background generation thread."""
        if self.stop_generation:
            self.stop_generation.set()
        if self.generator_thread and self.generator_thread.is_alive():
            self.generator_thread.join(timeout=2)

    def get_next_frame(self, timeout: float = 0.1) -> tuple | None:
        """Get next frame from queue (non-blocking with timeout)."""
        if self.frame_queue is None:
            return None
        
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None


def main(generator=None):
    """Main entry point for ASCII Dream TUI."""
    app = ASCIIDreamApp(generator=generator)
    result = app.run()
    if result:
        print(result)
    return 0


# Modal entrypoint for running with: modal run ascii_dream.tui
@modal_app.local_entrypoint()
def tui_main():
    """Modal-decorated entry point - initializes generator in Modal context."""
    # Get the generator while we're in the Modal app context
    generator = get_generator()
    return main(generator=generator)


def cli_entrypoint():
    """
    CLI wrapper entry point for 'ascii-dream' command.
    
    This function is called when user types 'ascii-dream' after pip install.
    It automatically wraps the call in 'modal run' to provide GPU context.
    """
    import subprocess
    import shutil
    
    # Check if modal CLI is installed
    if not shutil.which('modal'):
        print("❌ Error: Modal CLI not found!")
        print("   Please install it: pip install modal")
        print("   Then authenticate: modal setup")
        sys.exit(1)
    
    # Run the app via modal
    try:
        # Use -m to run as module (cleaner than file path)
        result = subprocess.run(
            ['modal', 'run', '-m', 'ascii_dream.tui'],
            check=False  # Don't raise on non-zero exit
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        # User pressed Ctrl+C - clean exit
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error launching ASCII Dream: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Running without Modal - generator will be None
    sys.exit(main())
