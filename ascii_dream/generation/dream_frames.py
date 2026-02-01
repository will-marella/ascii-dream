"""
Frame sequence generator for dream-like animations using correlated noise.
"""
import math
from typing import List, Tuple, Iterator
import random


class DreamFrameGenerator:
    """Generates frame sequences with correlated noise for dream-like movement."""
    
    def __init__(
        self,
        num_frames: int = 30,
        movement_type: str = "floating",
        intensity: float = 0.1,
        seed_base: int | None = None,
    ):
        """
        Initialize dream frame generator.
        
        Args:
            num_frames: Number of frames in the sequence
            movement_type: Type of movement ("floating", "pulsing", "rotating", "morphing")
            intensity: Movement intensity (0.01 to 0.5)
            seed_base: Base seed for noise generation (None = random)
        """
        self.num_frames = num_frames
        self.movement_type = movement_type
        self.intensity = max(0.01, min(0.5, intensity))
        
        # Use consistent base seed for all frames if provided
        if seed_base is None:
            seed_base = random.randint(0, 2**31 - 1)
        self.seed_base = seed_base
        
    def _get_frame_seed(self, frame_index: int) -> int:
        """Generate correlated seed for frame based on movement type."""
        # Start with base seed, add frame-based variation
        if self.movement_type == "floating":
            # Gentle drift - use base + small offset
            return self.seed_base + (frame_index * 7)
            
        elif self.movement_type == "pulsing":
            # Breathing effect - sinusoidal variation
            pulse_offset = int(10 * math.sin(frame_index * 0.3))
            return self.seed_base + pulse_offset
            
        elif self.movement_type == "rotating":
            # Spinning effect - rotate through seeds
            return self.seed_base + (frame_index * 13)
            
        elif self.movement_type == "morphing":
            # Morphing between states - use larger but patterned changes
            morph_pattern = [0, 5, 15, 30, 50, 30, 15, 5, 0]
            return self.seed_base + morph_pattern[frame_index % len(morph_pattern)]
            
        else:
            # Default floating movement
            return self.seed_base + frame_index
    
    def generate_frame_sequence(self, prompt_generator) -> Iterator[Tuple[str, int, int | None]]:
        """
        Generate sequence of prompts with correlated seeds.
        
        Args:
            prompt_generator: Function that generates prompts for each frame
            
        Yields:
            Tuples of (prompt, frame_index, seed) for each frame
        """
        for frame_index in range(self.num_frames):
            # Generate prompt for this frame
            frame_prompt = prompt_generator(frame_index) if prompt_generator else f"Abstract dream frame {frame_index}"
            
            # Get correlated seed for this frame
            frame_seed = self._get_frame_seed(frame_index)
            
            yield (frame_prompt, frame_index, frame_seed)
    
    def get_movement_description(self) -> str:
        """Get human-readable description of movement type."""
        descriptions = {
            "floating": "gentle floating drift",
            "pulsing": "organic breathing pulse", 
            "rotating": "smooth spinning motion",
            "morphing": "fluid morphing transitions",
        }
        return descriptions.get(self.movement_type, "unknown movement")


def create_dream_prompt_evolver(base_prompt: str, movement_words: List[str] = None) -> callable:
    """
    Create a prompt evolution function for dream sequences.
    
    Args:
        base_prompt: Base prompt for all frames
        movement_words: List of movement descriptors to cycle through
        
    Returns:
        Function that takes frame_index and returns prompt
    """
    if movement_words is None:
        # Default movement words for dream-like evolution
        movement_words = ["floating", "drifting", "swirling", "pulsing", "flowing", "morphing"]
    
    def prompt_evolver(frame_index: int) -> str:
        # Cycle through movement words
        movement_word = movement_words[frame_index % len(movement_words)]
        return f"{base_prompt}, {movement_word}, dreamy, ethereal"
    
    return prompt_evolver


def create_static_prompt(base_prompt: str) -> callable:
    """
    Create a static prompt function for consistent frames.
    
    Args:
        base_prompt: Base prompt for all frames
        
    Returns:
        Function that returns the same prompt for all frames
    """
    def static_prompt(frame_index: int) -> str:
        return base_prompt
    
    return static_prompt