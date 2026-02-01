"""
Prompt evolution strategies for ASCII Dream.
"""
import random
from typing import Iterator
from itertools import cycle

# Journey templates
JOURNEYS = {
    "abstract": [
        "geometric {color} shapes flowing smoothly",
        "swirling {color} and {color2} patterns",
        "abstract {color} waves in motion",
        "crystalline {color} structures forming",
        "fluid {color} ribbons dancing",
        "scattered {color} particles coalescing",
        "radiating {color} energy patterns",
        "interlocking {color} geometric forms",
        "flowing {color} liquid streams",
        "dynamic {color} and {color2} composition",
    ],
    "nature": [
        "{element} in {color} light",
        "organic {element} patterns growing",
        "{element} flowing like {color} water",
        "ethereal {color} {element} swirling",
        "dreamy {element} in {color} mist",
        "{element} blooming with {color} energy",
        "wild {color} {element} dancing",
        "serene {element} in {color} atmosphere",
    ],
    "cosmic": [
        "{color} nebula swirling in space",
        "cosmic {color} energy flowing",
        "stellar {color} and {color2} clouds",
        "galactic {color} vortex spinning",
        "celestial {color} patterns forming",
        "astral {color} waves rippling",
        "interstellar {color} matter dispersing",
        "cosmic {color2} dust in {color} void",
    ],
    "liquid": [
        "{color} paint swirling in water",
        "liquid {color} and {color2} mixing",
        "flowing {color} ink dispersing",
        "{color} liquid marble patterns",
        "viscous {color} fluid in motion",
        "aquatic {color} and {color2} streams",
        "molten {color} material flowing",
        "fluid {color} dynamics in motion",
    ],
}

COLOR_PALETTE = [
    "blue",
    "purple",
    "orange",
    "red",
    "green",
    "turquoise",
    "magenta",
    "cyan",
    "amber",
    "violet",
    "crimson",
    "emerald",
    "golden",
    "silver",
    "coral",
    "indigo",
    "rose",
    "teal",
]

NATURE_ELEMENTS = [
    "leaves",
    "water",
    "fire",
    "clouds",
    "mountains",
    "flowers",
    "trees",
    "waves",
    "wind",
    "rain",
    "lightning",
    "mist",
]


class PromptEvolver:
    """Generates evolving prompts for endless ASCII art."""

    def __init__(self, journey: str = "abstract", start_prompt: str | None = None):
        """
        Initialize prompt evolver.

        Args:
            journey: Journey type (abstract, nature, cosmic, liquid)
            start_prompt: Optional custom starting prompt
        """
        self.journey = journey
        self.start_prompt = start_prompt

        if journey not in JOURNEYS:
            raise ValueError(
                f"Unknown journey '{journey}'. "
                f"Choose from: {', '.join(JOURNEYS.keys())}"
            )

    def evolve(self) -> Iterator[str]:
        """
        Generate infinite sequence of evolving prompts.

        Yields:
            Prompt strings
        """
        # Start with custom prompt if provided
        if self.start_prompt:
            yield self.start_prompt

        # Infinite cycle through journey templates
        templates = cycle(JOURNEYS[self.journey])

        while True:
            template = next(templates)

            # Fill template with random keywords
            prompt = template.format(
                color=random.choice(COLOR_PALETTE),
                color2=random.choice(COLOR_PALETTE),
                element=random.choice(NATURE_ELEMENTS),
            )

            yield prompt


def get_evolver(
    journey: str = "abstract", start_prompt: str | None = None, custom: bool = False
) -> Iterator[str]:
    """
    Factory function for prompt evolvers.

    Args:
        journey: Journey type
        start_prompt: Optional starting prompt
        custom: If True, only yields start_prompt repeatedly (no evolution)

    Returns:
        Iterator yielding prompts
    """
    if custom and start_prompt:
        # No evolution - just repeat the same prompt
        while True:
            yield start_prompt
    else:
        evolver = PromptEvolver(journey, start_prompt)
        yield from evolver.evolve()
