"""
CLI entry point for ASCII Dream.
"""
import argparse
import asyncio
import sys
import io
import os
from PIL import Image
from ..generation.modal_backend import app, get_generator
from ..generation.prompt_evolution import get_evolver
from ..generation.dream_frames import DreamFrameGenerator, create_dream_prompt_evolver, create_static_prompt
from ..rendering.ascii_converter import AsciiConverter
from ..rendering.terminal_display import TerminalDisplay
from ..queue import ImageQueue

# Suppress common ML library warnings for clean output
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def get_dimensions_for_aspect_ratio(aspect_ratio: str, fast: bool) -> tuple[int, int]:
    """
    Convert aspect ratio string to image dimensions.
    
    Args:
        aspect_ratio: String like "16:9", "1:1", etc.
        fast: Whether to use lower resolution for faster generation
        
    Returns:
        Tuple of (width, height) in pixels
    """
    # Base resolution - keeping around 512x512 total pixels for quality
    base_resolution = 256 if fast else 512
    
    # Aspect ratio mapping with reasonable resolutions
    aspect_ratios = {
        "1:1": (base_resolution, base_resolution),  # Square
        "16:9": (768 if not fast else 384, 432 if not fast else 216),  # Landscape widescreen
        "9:16": (432 if not fast else 216, 768 if not fast else 384),  # Portrait
        "4:3": (576 if not fast else 288, 432 if not fast else 216),  # Standard landscape
        "3:4": (432 if not fast else 216, 576 if not fast else 288),  # Standard portrait
    }
    
    return aspect_ratios.get(aspect_ratio, aspect_ratios["1:1"])


async def run_display_loop(
    queue: ImageQueue, converter: AsciiConverter, display: TerminalDisplay
):
    """
    Main display loop: consume from queue and render.

    Args:
        queue: Image queue
        converter: ASCII converter
        display: Terminal display manager
    """
    # Start live display frame
    display.start_live_display()

    try:
        while True:
            # Check if queue is empty
            if queue.empty():
                display.show_generating()
                await asyncio.sleep(0.5)
                continue

            # Get next image
            image = await queue.get()
            
            # Handle prompt extraction if it's a tuple (backwards compatibility)
            prompt = None
            actual_image = image
            
            # Convert to ASCII art
            ascii_art = converter.convert(actual_image)

            # Display in the frame (updates in place)
            display.show(ascii_art, prompt or "Abstract Dream")

            # Wait for refresh interval
            await asyncio.sleep(display.refresh_rate)

    except asyncio.CancelledError:
        # Clean shutdown
        display.stop_live_display()
    finally:
        display.stop_live_display()


class ModalClientWrapper:
    """Wrapper to make Modal generator work with queue system."""

    def __init__(self, generator):
        self.generator = generator

    async def generate(
        self, prompt: str, width: int = 512, height: int = 512, seed: int | None = None
    ) -> Image.Image:
        """Generate image asynchronously."""
        # Async call to Modal (note: backend expects prompt, height, width, seed)
        image_bytes = await self.generator.generate.remote.aio(prompt, height, width, seed)
        # Deserialize bytes to PIL Image
        return Image.open(io.BytesIO(image_bytes))


async def async_main(args):
    """Async main function (runs within Modal app context)."""
    display = TerminalDisplay(refresh_rate=args.speed)

    # Show startup screen
    display.show_startup()

    # Get Modal generator instance
    generator = get_generator()

    # Show cold start warning on first run
    display.show_cold_start()

    # Determine image size based on aspect ratio and speed
    image_size = get_dimensions_for_aspect_ratio(args.aspect_ratio, args.fast)

    # Wrap generator for queue
    client = ModalClientWrapper(generator)

    # Get prompt evolver
    prompt_iter = get_evolver(
        journey=args.journey,
        start_prompt=args.prompt,
        custom=(args.prompt is not None and not args.evolve),
    )

    # Create queue for multiple frames (or single image)
    queue = ImageQueue(
        generator=client,
        prompt_iterator=prompt_iter,
        queue_depth=2,
        image_size=image_size,
        frames_per_cycle=args.frames,
    )
    
    # Display frame count info if multiple frames
    if args.frames > 1:
        print(f"🎬 Cycling through {args.frames} images")

    # Start producer
    queue.start()

    # Wait for initial prefill
    await queue.prefill()

    # Create converter
    converter = AsciiConverter(width=args.width)

    # Run display loop
    display_task = asyncio.create_task(run_display_loop(queue, converter, display))

    try:
        await display_task
    except KeyboardInterrupt:
        # Graceful shutdown
        display_task.cancel()
        try:
            await display_task
        except asyncio.CancelledError:
            pass
        await queue.stop()
        display.goodbye()
        return 0


@app.local_entrypoint()
def main(*raw_args):
    """
    CLI entry point (Modal local entrypoint).

    Accepts *raw_args so Modal skips automatic CLI parsing and lets argparse handle it.
    """
    parser = argparse.ArgumentParser(
        description="ASCII Dream - Endless evolving ASCII art using AI"
    )

    parser.add_argument(
        "--prompt", type=str, help="Starting prompt (default: journey-based evolution)"
    )

    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Terminal width in characters (default: auto-detect)",
    )

    parser.add_argument(
        "--speed",
        type=float,
        default=3.0,
        help="Seconds between frames (default: 3.0)",
    )

    parser.add_argument(
        "--journey",
        type=str,
        default="abstract",
        choices=["abstract", "nature", "cosmic", "liquid"],
        help="Evolution journey theme (default: abstract)",
    )

    parser.add_argument(
        "--evolve",
        action="store_true",
        help="Evolve from starting prompt (default: static if --prompt given)",
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use 256x256 images for faster generation (default: 512x512)",
    )

    parser.add_argument(
        "--aspect-ratio",
        type=str,
        default="1:1",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
        help="Aspect ratio for generated images (default: 1:1 square)",
    )

    parser.add_argument(
        "--frames",
        type=int,
        default=1,
        help="Number of images to generate and cycle through (default: 1)",
    )

    # Parse the raw args passed by Modal
    args = parser.parse_args(raw_args)

    # Run async main
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        return 0
