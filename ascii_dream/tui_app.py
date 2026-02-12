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

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical, Center
    from textual.widgets import Static, Button, Label, OptionList
    from textual.widgets.option_list import Option
    from textual.screen import Screen
    from textual import on, work
    from textual.binding import Binding
    from textual.worker import Worker, get_current_worker

    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    print(f"Required library not available: {e}")
    print("Please install with: pip install textual")
    sys.exit(1)

from PIL import Image
from rich.text import Text

# Import Modal backend and generation components
from .generation.modal_backend import app as modal_app, get_generator
from .generation.prompt_evolution import get_evolver
from .rendering.ascii_converter import AsciiConverter


# ASCII art title for ASCII DREAM
ASCII_TITLE = """ █████╗ ███████╗ ██████╗██╗██╗    ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗
██╔══██╗██╔════╝██╔════╝██║██║    ██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║
███████║███████╗██║     ██║██║    ██║  ██║██████╔╝█████╗  ███████║██╔████╔██║
██╔══██║╚════██║██║     ██║██║    ██║  ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║
██║  ██║███████║╚██████╗██║██║    ██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"""


def get_dimensions_for_aspect_ratio(aspect_ratio: str, fast: bool) -> tuple[int, int]:
    """Convert aspect ratio string to image dimensions."""
    base_resolution = 256 if fast else 512
    
    aspect_ratios = {
        "1:1": (base_resolution, base_resolution),
        "16:9": (768 if not fast else 384, 432 if not fast else 216),
        "9:16": (432 if not fast else 216, 768 if not fast else 384),
        "4:3": (576 if not fast else 288, 432 if not fast else 216),
        "3:4": (432 if not fast else 216, 576 if not fast else 288),
    }
    
    return aspect_ratios.get(aspect_ratio, aspect_ratios["1:1"])


class MainMenuScreen(Screen):
    """Main menu screen."""

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

    #menu-container {
        width: auto;
        height: auto;
        align: center middle;
    }

    OptionList {
        width: 50;
        height: auto;
        background: $surface;
        border: none;
    }

    OptionList:focus {
        border: none;
    }

    OptionList > .option-list--option {
        background: transparent;
        color: $text;
    }

    OptionList > .option-list--option-highlighted {
        background: transparent;
        color: $warning;
        text-style: bold;
    }

    #controls {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("escape", "quit", "Quit", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the main menu."""
        yield Static(ASCII_TITLE, id="title")
        yield Static("Generate beautiful, evolving ASCII art from AI dreams", id="tagline")

        with Container(id="menu-container"):
            yield OptionList(
                Option("Start Dream", id="start"),
                Option("Configure Settings", id="settings"),
                Option("Quit", id="quit"),
            )

        yield Static("↑/↓: Navigate  •  Enter: Select  •  Q/Esc: Quit", id="controls")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle menu selection."""
        if event.option.id == "quit":
            self.app.exit()
        elif event.option.id == "settings":
            self.app.push_screen(SettingsScreen())
        elif event.option.id == "start":
            self.app.push_screen(DreamScreen())


class SettingsScreen(Screen):
    """Settings configuration screen."""

    CSS = """
    SettingsScreen {
        align: center middle;
        background: $background;
    }

    #settings-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    #settings-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }

    .setting-row {
        width: 100%;
        height: auto;
        color: $text;
    }

    .setting-label {
        color: $text-muted;
    }

    .setting-value {
        color: $accent;
    }

    #settings-instructions {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 1;
    }

    #settings-options {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin-top: 1;
        margin-bottom: 1;
    }

    #back-hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
        Binding("1", "config_prompt", "Prompt", show=False),
        Binding("2", "config_ratio", "Ratio", show=False),
        Binding("3", "config_fps", "FPS", show=False),
        Binding("4", "config_quality", "Quality", show=False),
        Binding("5", "config_theme", "Theme", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        with Center():
            yield Static("⚙ Settings", id="settings-title")

            with Container(id="settings-box"):
                app = self.app
                if hasattr(app, 'config'):
                    config = app.config
                    yield Static("", classes="setting-row")
                    yield Static(
                        f"[dim]Prompt:[/dim] [cyan]{config['prompt'] if config['prompt'] else '(journey mode)'}[/cyan]",
                        classes="setting-row"
                    )
                    yield Static(
                        f"[dim]Aspect Ratio:[/dim] [cyan]{config['aspect_ratio']}[/cyan]",
                        classes="setting-row"
                    )
                    yield Static(
                        f"[dim]Frame Rate:[/dim] [cyan]{config['fps']} fps[/cyan]",
                        classes="setting-row"
                    )
                    yield Static(
                        f"[dim]Quality:[/dim] [cyan]{'Fast' if config['fast'] else 'Normal'}[/cyan]",
                        classes="setting-row"
                    )
                    yield Static(
                        f"[dim]Journey Theme:[/dim] [cyan]{config['journey'].title()}[/cyan]",
                        classes="setting-row"
                    )
                    yield Static("", classes="setting-row")

            yield Static("Press 1-5 to configure options  •  Esc to go back", id="settings-instructions")
            yield Static("[yellow]1[/yellow][dim]:Prompt  [/dim][yellow]2[/yellow][dim]:Ratio  [/dim][yellow]3[/yellow][dim]:FPS  [/dim][yellow]4[/yellow][dim]:Quality  [/dim][yellow]5[/yellow][dim]:Theme[/dim]", id="settings-options")

    def action_config_prompt(self) -> None:
        """Configure prompt."""
        self.app.push_screen(ConfigPromptScreen())

    def action_config_ratio(self) -> None:
        """Configure aspect ratio."""
        self.app.push_screen(ConfigRatioScreen())

    def action_config_fps(self) -> None:
        """Configure FPS."""
        self.app.push_screen(ConfigFPSScreen())

    def action_config_quality(self) -> None:
        """Configure quality."""
        self.app.push_screen(ConfigQualityScreen())

    def action_config_theme(self) -> None:
        """Configure theme."""
        self.app.push_screen(ConfigThemeScreen())


class ConfigPromptScreen(Screen):
    """Prompt configuration screen."""

    CSS = """
    ConfigPromptScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 2;
    }

    #config-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose prompt config screen."""
        with Center():
            yield Static("Configure Prompt", id="config-title")
            with Container(id="config-box"):
                yield Static("\nLeave empty for Journey Mode (evolving prompts)\n", classes="setting-row")
                yield Static("Or set a custom prompt in settings\n", classes="setting-row")
                current = self.app.config['prompt'] if self.app.config['prompt'] else "(journey mode)"
                yield Static(f"[dim]Current:[/dim] [cyan]{current}[/cyan]\n", classes="setting-row")
            yield Static("Press Esc to go back", id="hint")


class ConfigRatioScreen(Screen):
    """Aspect ratio configuration screen."""

    CSS = """
    ConfigRatioScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 40;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose ratio config screen."""
        with Center():
            yield Static("Configure Aspect Ratio", id="config-title")

            current = self.app.config['aspect_ratio']
            options = ["1:1", "16:9", "9:16", "4:3", "3:4"]

            yield OptionList(
                *[Option(f"{r}{' ← CURRENT' if r == current else ''}", id=r) for r in options]
            )
            yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle ratio selection."""
        self.app.config['aspect_ratio'] = event.option.id
        self.app.pop_screen()


class ConfigFPSScreen(Screen):
    """FPS configuration screen."""

    CSS = """
    ConfigFPSScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 40;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose FPS config screen."""
        with Center():
            yield Static("Configure Frame Rate", id="config-title")
            
            current = self.app.config['fps']
            fps_options = [0.5, 1.0, 2.0, 3.0, 5.0]
            
            yield OptionList(
                *[Option(f"{f} fps{' ← CURRENT' if f == current else ''}", id=str(f)) for f in fps_options]
            )
            yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle FPS selection."""
        self.app.config['fps'] = float(event.option.id)
        self.app.pop_screen()


class ConfigQualityScreen(Screen):
    """Quality configuration screen."""

    CSS = """
    ConfigQualityScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose quality config screen."""
        with Center():
            yield Static("Configure Quality", id="config-title")

            current = "fast" if self.app.config['fast'] else "normal"

            yield OptionList(
                Option(f"Fast (256x256, quicker){' ← CURRENT' if current == 'fast' else ''}", id="fast"),
                Option(f"Normal (512x512, higher quality){' ← CURRENT' if current == 'normal' else ''}", id="normal"),
            )
            yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle quality selection."""
        self.app.config['fast'] = (event.option.id == "fast")
        self.app.pop_screen()


class ConfigThemeScreen(Screen):
    """Theme configuration screen."""

    CSS = """
    ConfigThemeScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 40;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose theme config screen."""
        with Center():
            yield Static("Configure Journey Theme", id="config-title")

            current = self.app.config['journey']
            themes = ["abstract", "nature", "cosmic", "liquid"]

            yield OptionList(
                *[Option(f"{t.title()}{' ← CURRENT' if t == current else ''}", id=t) for t in themes]
            )
            yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle theme selection."""
        self.app.config['journey'] = event.option.id
        self.app.pop_screen()


class DreamScreen(Screen):
    """Dream configuration confirmation screen."""

    CSS = """
    DreamScreen {
        align: center middle;
        background: $background;
    }

    #dream-box {
        width: 70;
        height: auto;
        border: solid $success;
        padding: 2 4;
        background: $surface;
    }

    .dream-row {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 1;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "app.quit", "Quit", show=False),
        Binding("enter", "start_generation", "Start", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose dream screen."""
        with Center():
            with Container(id="dream-box"):
                yield Static("[bold green]Dream Configuration Ready![/bold green]", classes="dream-row")
                yield Static("", classes="dream-row")

                config = self.app.config
                yield Static(f"Prompt: {config['prompt'] if config['prompt'] else 'Journey Mode'}", classes="dream-row")
                yield Static(f"Aspect Ratio: {config['aspect_ratio']}", classes="dream-row")
                yield Static(f"Quality: {'Fast' if config['fast'] else 'Normal'}", classes="dream-row")
                yield Static(f"FPS: {config['fps']}", classes="dream-row")
                yield Static("", classes="dream-row")
                yield Static("[bold cyan]Press Enter to start dreaming![/bold cyan]", classes="dream-row")

            yield Static("Enter: Start  •  Esc: Back  •  Q: Quit", id="hint")

    def action_start_generation(self) -> None:
        """Start the actual dream generation."""
        # Push loading screen and start generation worker
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
                self.app.call_from_thread(self.app.pop_screen)
                self.app.call_from_thread(self.app.notify, "No frames generated", "error")
        except Exception as e:
            self.app.call_from_thread(self.app.pop_screen)
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
        Binding("escape", "stop_and_back", "Back", show=False),
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
        fps = self.app.config['fps']
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
        self.app.pop_screen()

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
        self.config = {
            'prompt': '',
            'aspect_ratio': '1:1',
            'fast': True,  # Default to fast for better UX
            'fps': 2.0,
            'journey': 'abstract',
            'custom_prompt': False
        }
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
        config = self.config
        
        # Get dimensions
        width, height = get_dimensions_for_aspect_ratio(
            config['aspect_ratio'],
            config['fast']
        )
        
        # Initialize converter
        self.converter = AsciiConverter(width=80)
        self.image_width = width
        self.image_height = height
        
        # Get prompts - infinite iterator
        self.prompt_iterator = get_evolver(
            journey=config['journey'],
            start_prompt=config['prompt'] if config['prompt'] else None,
            custom=bool(config['prompt']),
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


# Modal entrypoint for running with: modal run ascii_dream/tui_app.py
@modal_app.local_entrypoint()
def tui_main():
    """Modal-decorated entry point - initializes generator in Modal context."""
    # Get the generator while we're in the Modal app context
    generator = get_generator()
    return main(generator=generator)


if __name__ == "__main__":
    # Running without Modal - generator will be None
    sys.exit(main())
