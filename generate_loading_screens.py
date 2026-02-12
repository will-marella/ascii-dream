#!/usr/bin/env python3
"""
Generate static ASCII art loading screens for the TUI app.
"""
from pathlib import Path

def create_loading_screens():
    """Generate backup ASCII art for loading screens."""
    output_dir = Path("ascii_dream/static/loading_screens")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Animated timer pattern
    pattern = """         .  :  .  :  .  :  .  :  .  :  .
        .'`.·.'`.·.'`.·.'`.·.'`.·.'`.·.'`.
       ·    ·    ·    ·    ·    ·    ·    ·
      .'  .'  .'  .'  .'  .'  .'  .'  .'  .
     ·    ·    ·  Dream  ·    ·    ·    ·
    .'  .'  .'  Loading...  .'  .'  .'  .
     ·    ·    ·    ·    ·    ·    ·    ·
      .'  .'  .'  .'  .'  .'  .'  .'  .'
       ·    ·    ·    ·    ·    ·    ·
        .'`.·.'`.·.'`.·.'`.·.'`.·.'`.·.'
         :  .  :  .  :  .  :  .  :  .  :

    Connecting to the cloud GPU..."""

    with open(output_dir / "timer_pattern.txt", "w") as f:
        f.write(pattern.strip())

    print(f"✓ Created timer_pattern.txt in {output_dir}")

if __name__ == "__main__":
    create_loading_screens()
