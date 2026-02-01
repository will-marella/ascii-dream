"""
Convert PIL Images to colored ASCII art for terminal display using ascii-magic.
"""
from PIL import Image
from ascii_magic import AsciiArt, Back
from rich.text import Text
from rich.console import Console
import io
import sys
import shutil


class AsciiConverter:
    """Converts PIL Images to terminal-renderable ASCII art using ascii-magic."""

    def __init__(self, width: int | None = None):
        """
        Initialize converter.

        Args:
            width: Target width in characters (None = auto-detect terminal width)
        """
        # Auto-detect terminal width if not specified
        if width is None:
            terminal_width = shutil.get_terminal_size().columns
            # Target ~70% of terminal width for nice framing
            self.width = min(int(terminal_width * 0.7), 80)
        else:
            self.width = width

        self.console = Console()

    def convert(self, image: Image.Image) -> str:
        """
        Convert PIL Image to colored ASCII art using ascii-magic.

        Args:
            image: PIL Image from Modal

        Returns:
            ASCII art string (ascii-magic prints directly)
        """
        # Pre-resize image for better ASCII conversion
        # Let ascii-magic handle aspect ratio with width_ratio parameter
        original_width, original_height = image.size

        # Create AsciiArt from cropped PIL Image
        art = AsciiArt.from_pillow_image(image)

        # Capture the output instead of printing directly
        old_stdout = sys.stdout
        sys.stdout = output = io.StringIO()

        try:
            # Generate colored ASCII art to terminal
            # width_ratio=2.2 to compensate for tall ASCII characters
            art.to_terminal(columns=self.width, width_ratio=2.2)
            result = output.getvalue()
        finally:
            sys.stdout = old_stdout

        return result
