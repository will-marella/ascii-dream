#!/usr/bin/env python3
"""
Test ASCII conversion with a sample image.
"""
from PIL import Image
from ascii_dream.rendering.ascii_converter import AsciiConverter
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

# Load the test image
image_path = "ascii_dream/practice-images/image.webp"
print(f"Loading image: {image_path}")
image = Image.open(image_path)

print(f"Image size: {image.size}")
print(f"Image mode: {image.mode}")

# Create ASCII converter (auto terminal width)
converter = AsciiConverter(width=None)

print("\nConverting to ASCII art...")
ascii_art = converter.convert(image)

# Display using Rich (like the TUI does)
console = Console()
console.clear()

# Create Text object from ANSI art (handles colors)
text_art = Text.from_ansi(ascii_art.rstrip())

# Add a caption
text_art.append("\n\n")
text_art.append("Test Image - ASCII Conversion", style="dim italic")

# Display in a panel
panel = Panel(
    text_art,
    title="[bold cyan]ASCII DREAM - Test[/bold cyan]",
    border_style="cyan",
    padding=(1, 2)
)

console.print(panel)
print("\n✓ ASCII conversion successful!")
