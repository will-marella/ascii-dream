"""
Terminal display management for ASCII Dream.
"""
import os
import sys
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align


class TerminalDisplay:
    """Manages terminal output and display loop."""

    def __init__(self, refresh_rate: float = 3.0, fps: float = 2.0):
        """
        Initialize display.

        Args:
            refresh_rate: Seconds between frame updates (legacy, for single image mode)
            fps: Frames per second for animation mode
        """
        self.console = Console()
        self.refresh_rate = refresh_rate
        self.fps = fps
        self.current_prompt = ""
        self.live_display = None
        self.frame_buffer = []
        self.animation_mode = False
        self.current_frame_index = 0

    def show_startup(self):
        """Show startup loading screen."""
        self.console.clear()

        startup_text = Text.from_markup(
            "[bold cyan]ASCII DREAM[/bold cyan]\n\n"
            "[dim]Loading...[/dim]"
        )

        panel = Panel(startup_text, border_style="cyan", padding=(1, 2))

        self.console.print(panel)

    def show_cold_start(self):
        """Show cold start loading (first run takes ~50s)."""
        self.console.clear()

        # Show a clean loading message
        self.console.print("\n")
        self.console.print("[bold cyan]ASCII DREAM[/bold cyan]", justify="center")
        self.console.print("\n")
        self.console.print("[dim]Loading AI model and generating images...[/dim]", justify="center")
        self.console.print("[dim](First run takes ~50s, then much faster)[/dim]", justify="center")
        self.console.print("\n")

    def start_live_display(self):
        """Start the live display context for updating frames."""
        if self.live_display is None:
            # Create a live display that we'll update in place
            self.live_display = Live(
                self._create_frame("", "Initializing..."),
                console=self.console,
                refresh_per_second=4,
                screen=False,
            )
            self.live_display.start()

    def stop_live_display(self):
        """Stop the live display."""
        if self.live_display:
            self.live_display.stop()
            self.live_display = None

    def _create_frame(self, ascii_art: str, prompt: str) -> Panel:
        """
        Create a framed panel with ASCII art.

        Args:
            ascii_art: ASCII art string
            prompt: Current prompt

        Returns:
            Panel with framed content
        """
        # Build content with ASCII art and caption
        content_parts = []

        if ascii_art:
            # Add ASCII art
            content_parts.append(Text.from_ansi(ascii_art.rstrip()))
        else:
            content_parts.append(Text("", style="dim"))

        # Add spacing
        content_parts.append(Text(""))

        # Add prompt caption
        caption = Text(prompt, style="dim italic", justify="center")
        content_parts.append(caption)

        # Add controls hint
        hint = Text("Press Ctrl+C to exit", style="dim", justify="center")
        content_parts.append(hint)

        # Group all content
        content = Group(*content_parts)

        # Create panel with fixed frame
        return Panel(
            content,
            title="[bold cyan]ASCII DREAM[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

    def show(self, ascii_art: str, prompt: str):
        """
        Display ASCII art frame (updates in place).

        Args:
            ascii_art: Rendered ASCII art string from converter (with ANSI colors)
            prompt: Current prompt for caption
        """
        self.current_prompt = prompt

        # Update the live display with new content
        if self.live_display:
            self.live_display.update(self._create_frame(ascii_art, prompt))

    def show_generating(self):
        """Show 'generating' indicator if queue runs dry."""
        if self.live_display:
            text = Text("Generating next frame...", style="yellow", justify="center")
            self.live_display.update(
                Panel(
                    text,
                    title="[bold cyan]ASCII DREAM[/bold cyan]",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )

    def show_error(self, error: str):
        """Show error message."""
        self.console.clear()

        error_text = Text.from_markup(f"[bold red]Error:[/bold red]\n\n{error}")

        self.console.print(Panel(error_text, border_style="red"))

    def start_animation(self, frame_count: int):
        """Initialize animation mode with frame buffer."""
        self.animation_mode = True
        self.frame_buffer = [""] * frame_count
        self.current_frame_index = 0
        
        # Use FPS-based refresh instead of refresh_rate
        self.refresh_rate = 1.0 / self.fps
        
    def add_frame(self, ascii_art: str, prompt: str, frame_index: int):
        """Add a frame to the animation buffer."""
        if frame_index < len(self.frame_buffer):
            self.frame_buffer[frame_index] = (ascii_art, prompt)
    
    def show_next_frame(self):
        """Display the next frame in animation sequence."""
        if not self.frame_buffer or not self.animation_mode:
            return False
            
        # Get current frame
        ascii_art, prompt = self.frame_buffer[self.current_frame_index]
        
        # Update display
        if self.live_display:
            self.live_display.update(self._create_frame(ascii_art, prompt))
        
        # Move to next frame
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frame_buffer)
        return True
    
    def is_animation_ready(self) -> bool:
        """Check if all frames are buffered and ready for playback."""
        return self.animation_mode and all(frame[0] != "" for frame in self.frame_buffer)

    def goodbye(self):
        """Show goodbye message on exit."""
        if self.live_display:
            self.stop_live_display()

        self.console.clear()

        goodbye_text = Text.from_markup(
            "[bold cyan]ASCII DREAM[/bold cyan]\n\n"
            "[dim]Thanks for dreaming with us.[/dim]"
        )

        self.console.print(Panel(goodbye_text, border_style="cyan"))

    def show_generating(self):
        """Show 'generating' indicator if queue runs dry."""
        self.console.clear()

        text = Text.from_markup(
            "[bold yellow]Generating next frame...[/bold yellow]\n"
            "[dim]Queue empty, please wait[/dim]"
        )

        self.console.print(Panel(text, border_style="yellow"))

    def show_error(self, error: str):
        """Show error message."""
        self.console.clear()

        error_text = Text.from_markup(f"[bold red]Error:[/bold red]\n\n{error}")

        self.console.print(Panel(error_text, border_style="red"))

    def goodbye(self):
        """Show goodbye message on exit."""
        self.console.clear()

        goodbye_text = Text.from_markup(
            "[bold cyan]ASCII DREAM[/bold cyan]\n\n"
            "[dim]Thanks for dreaming with us.[/dim]"
        )

        self.console.print(Panel(goodbye_text, border_style="cyan"))
