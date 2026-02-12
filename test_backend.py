#!/usr/bin/env python3
"""
Test the Modal backend directly without TUI.
Run with: modal run test_backend.py
"""
from ascii_dream.generation.modal_backend import app, get_generator
from ascii_dream.rendering.ascii_converter import AsciiConverter
from PIL import Image
import io


@app.local_entrypoint()
def main():
    print('Getting generator...')
    generator = get_generator()

    print('Generating image (this may take ~50s on first run)...')
    image_bytes = generator.generate.remote(
        'abstract colorful geometric shapes flowing smoothly', 
        height=256, 
        width=256
    )

    print(f'Got {len(image_bytes)} bytes')

    # Convert to image
    image = Image.open(io.BytesIO(image_bytes))
    print(f'Image size: {image.size}')

    # Convert to ASCII
    print('\nConverting to ASCII art...\n')
    converter = AsciiConverter(width=60)
    ascii_art = converter.convert(image)
    print(ascii_art)
    print('\nDone!')
