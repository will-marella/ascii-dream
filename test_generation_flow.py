#!/usr/bin/env python3
"""
Test the full generation flow without TUI interaction.
Run with: modal run test_generation_flow.py
"""
from ascii_dream.generation.modal_backend import app, get_generator
from ascii_dream.generation.prompt_evolution import get_evolver
from ascii_dream.rendering.ascii_converter import AsciiConverter
from PIL import Image
import io
import time


@app.local_entrypoint()
def main():
    print('=' * 60)
    print('ASCII DREAM - Generation Flow Test')
    print('=' * 60)
    
    # Config (same defaults as TUI)
    config = {
        'prompt': '',
        'aspect_ratio': '1:1',
        'frames': 3,
        'fast': True,
        'fps': 2.0,
        'journey': 'cosmic',
    }
    
    # Get dimensions
    width, height = 256, 256  # Fast mode
    
    print(f'\nConfig:')
    print(f'  Journey: {config["journey"]}')
    print(f'  Frames: {config["frames"]}')
    print(f'  Size: {width}x{height}')
    print()
    
    # Initialize
    print('Initializing generator...')
    generator = get_generator()
    converter = AsciiConverter(width=70)
    
    # Get prompts
    prompt_iter = get_evolver(
        journey=config['journey'],
        start_prompt=config['prompt'] if config['prompt'] else None,
        custom=bool(config['prompt']),
    )
    
    frames = []
    
    # Generate frames
    for i in range(config['frames']):
        prompt = next(prompt_iter)
        print(f'\n[Frame {i+1}/{config["frames"]}] Generating: "{prompt}"')
        
        start = time.time()
        image_bytes = generator.generate.remote(prompt, height=height, width=width)
        elapsed = time.time() - start
        
        print(f'  Generated in {elapsed:.1f}s ({len(image_bytes)} bytes)')
        
        # Convert to ASCII
        image = Image.open(io.BytesIO(image_bytes))
        ascii_art = converter.convert(image)
        frames.append((ascii_art, prompt))
    
    # Display frames
    print('\n' + '=' * 60)
    print('GENERATED FRAMES:')
    print('=' * 60)
    
    for i, (ascii_art, prompt) in enumerate(frames):
        print(f'\n--- Frame {i+1}: {prompt} ---\n')
        print(ascii_art)
    
    print('\n' + '=' * 60)
    print('SUCCESS! All frames generated.')
    print('=' * 60)
