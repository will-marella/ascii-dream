#!/usr/bin/env python3
"""
ASCII Dream - Beautiful TUI application (prototype version).
"""
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich library not available. Please install with: pip install rich")
    sys.exit(1)


class ASCIIDreamTUI:
    """Main ASCII Dream TUI application."""
    
    def __init__(self):
        if not RICH_AVAILABLE:
            raise ImportError("Rich library required for TUI")
        
        self.console = Console()
        self.config = {
            'prompt': '',
            'aspect_ratio': '1:1',
            'frames': 3,
            'fast': False,
            'fps': 2.0,
            'journey': 'abstract',
            'custom_prompt': False
        }
    
    def show_main_menu(self):
        """Display the main ASCII Dream interface."""
        self.console.clear()
        
        # ASCII Art Title
        title_art = """
╭──────────────────────────────────────────────────────────────╮
│                                                      │
│  🌌 ASCII DREAM 🌌                                      │
│                                                      │
│  Generate beautiful, evolving ASCII art from AI dreams     │
│                                                      │
╰──────────────────────────────────────────────────────────────╯
"""
        
        # Menu Options
        menu_text = """
📋 Configuration Options:

┌─ Prompt ─────────────────────────────────┐
│                                      │
│ 1. Set Prompt: [bold cyan]{}[/bold cyan]                    │
│                                      │
└───────────────────────────────────────┘

┌─ Display ──────────────────────────────┐
│                                      │
│ 2. Aspect Ratio: [bold cyan]{}[/bold cyan]                     │
│ 3. Frame Count: [bold cyan]{}[/bold cyan]                        │
│ 4. Frame Rate: [bold cyan]{}[/bold cyan] fps                        │
│ 5. Quality: [bold cyan]{}[/bold cyan]                             │
│                                      │
└───────────────────────────────────────┘

┌─ Theme ────────────────────────────────┐
│                                      │
│ 6. Journey Theme: [bold cyan]{}[/bold cyan]                     │
│                                      │
└───────────────────────────────────────┘

[dim]Press 1-6 to configure, 'D' to Dream, 'Q' to quit[/dim]
""".format(
                self.config['prompt'] if self.config['prompt'] else '(default)',
                self.config['aspect_ratio'],
                self.config['frames'],
                self.config['fps'],
                'Fast' if self.config['fast'] else 'Normal',
                self.config['journey'].title()
            )
        
        full_screen = title_art + "\n" + menu_text
        self.console.print(full_screen)
        
        return True  # Continue loop
    
    def get_user_input(self):
        """Get user input safely."""
        try:
            return input("> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            return 'Q'
    
    def configure_prompt(self):
        """Configure prompt input."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Configure Prompt[/bold cyan]", border_style="cyan"))
        self.console.print("\n[dim]Enter your dream prompt (or 'journey' for evolving themes):[/dim]")
        
        prompt = self.get_user_input()
        if prompt == 'Q':
            return True  # Continue
        elif prompt.lower() == 'journey':
            self.config['custom_prompt'] = False
        elif prompt:
            self.config['prompt'] = prompt
            self.config['custom_prompt'] = True
        
        self.show_info(f"Prompt set to: {self.config['prompt'] if self.config['custom_prompt'] else 'Journey Mode'}")
        return True
    
    def configure_aspect_ratio(self):
        """Configure aspect ratio."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Configure Aspect Ratio[/bold cyan]", border_style="cyan"))
        
        options = ["1:1", "16:9", "9:16", "4:3", "3:4"]
        self.console.print("\n[dim]Available aspect ratios:[/dim]")
        for i, ratio in enumerate(options, 1):
            current = " ← CURRENT" if ratio == self.config['aspect_ratio'] else ""
            self.console.print(f"{i}. {ratio}{current}")
        
        choice = self.get_user_input()
        if choice == 'Q':
            return True
        elif choice.isdigit() and 1 <= int(choice) <= len(options):
            self.config['aspect_ratio'] = options[int(choice) - 1]
            self.show_info(f"Aspect ratio set to: {self.config['aspect_ratio']}")
        else:
            self.show_error("Invalid choice.")
        return True
    
    def configure_frames(self):
        """Configure frame count."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Configure Frame Count[/bold cyan]", border_style="cyan"))
        self.console.print("\n[dim]Number of frames to generate and cycle (1-50):[/dim]")
        self.console.print(f"[dim]Current: {self.config['frames']}[/dim]")
        
        frames = self.get_user_input()
        if frames == 'Q':
            return True
        elif frames.isdigit() and 1 <= int(frames) <= 50:
            self.config['frames'] = int(frames)
            self.show_info(f"Frame count set to: {self.config['frames']}")
        else:
            self.show_error("Please enter a number between 1 and 50.")
        return True
    
    def configure_fps(self):
        """Configure frame rate."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Configure Frame Rate[/bold cyan]", border_style="cyan"))
        self.console.print("\n[dim]Frames per second for dream cycling (0.5-5.0):[/dim]")
        self.console.print(f"[dim]Current: {self.config['fps']}[/dim]")
        
        try:
            fps = float(self.get_user_input())
            if fps == 'Q':
                return True
            elif 0.5 <= fps <= 5.0:
                self.config['fps'] = fps
                self.show_info(f"Frame rate set to: {self.config['fps']} fps")
            else:
                self.show_error("Please enter a value between 0.5 and 5.0.")
        except ValueError:
            self.show_error("Please enter a valid number.")
        return True
    
    def configure_quality(self):
        """Configure quality (fast/normal)."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Configure Quality[/bold cyan]", border_style="cyan"))
        self.console.print("\n[dim]1. Fast (256x256 base, quicker generation)[/dim]")
        self.console.print("[dim]2. Normal (512x512 base, higher quality)[/dim]")
        self.console.print(f"[dim]Current: {1 if self.config['fast'] else 2}. Fast{' ✓' if self.config['fast'] else ''} Normal{' ✓' if not self.config['fast'] else ''}[/dim]")
        
        choice = self.get_user_input()
        if choice == 'Q':
            return True
        elif choice == '1':
            self.config['fast'] = True
            self.show_info("Quality set to: Fast")
        elif choice == '2':
            self.config['fast'] = False
            self.show_info("Quality set to: Normal")
        else:
            self.show_error("Invalid choice.")
        return True
    
    def configure_journey(self):
        """Configure journey theme."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Configure Journey Theme[/bold cyan]", border_style="cyan"))
        
        themes = ["abstract", "nature", "cosmic", "liquid"]
        self.console.print("\n[dim]Available journey themes:[/dim]")
        for i, theme in enumerate(themes, 1):
            current = " ← CURRENT" if theme == self.config['journey'] else ""
            self.console.print(f"{i}. {theme.title()}{current}")
        
        choice = self.get_user_input()
        if choice == 'Q':
            return True
        elif choice.isdigit() and 1 <= int(choice) <= len(themes):
            self.config['journey'] = themes[int(choice) - 1]
            self.show_info(f"Journey theme set to: {self.config['journey'].title()}")
        else:
            self.show_error("Invalid choice.")
        return True
    
    def show_info(self, message: str):
        """Show info message."""
        self.console.print(Panel(f"[bold green]✓[/bold green] {message}", border_style="green"))
    
    def show_error(self, message: str):
        """Show error message."""
        self.console.print(Panel(f"[bold red]✗[/bold red] {message}", border_style="red"))
    
    def show_dream_loading(self):
        """Show dream loading screen."""
        self.console.clear()
        loading_text = """
╭──────────────────────────────────────────────────────────────╮
│                                                      │
│  🌌 ASCII DREAM 🌌                                      │
│                                                      │
│  Loading dream...                                      │
│  (Generating {} frames)                                  │
│                                                      │
╰──────────────────────────────────────────────────────────────╯
""".format(self.config['frames'])
        
        self.console.print(loading_text)
    
    def show_goodbye(self):
        """Show goodbye message."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]ASCII DREAM[/bold cyan]\n\n[dim]Thanks for dreaming with us.[/dim]", border_style="cyan"))
    
    def start_dream(self):
        """Start the dream (placeholder for now)."""
        if not self.config['custom_prompt']:
            self.show_error("Please set a prompt first (option 1)")
            return True
        
        self.show_dream_loading()
        
        # Placeholder for integration with backend
        info_text = f"""
[bold green]🎭 Dream Configuration Ready![/bold green]

[dim]Prompt:[/dim] {self.config['prompt']}
[dim]Aspect Ratio:[/dim] {self.config['aspect_ratio']}
[dim]Frames:[/dim] {self.config['frames']}
[dim]Quality:[/dim] {'Fast' if self.config['fast'] else 'Normal'}
[dim]FPS:[/dim] {self.config['fps']}

[dim]Press Enter to start the actual dream generation...[/dim]
"""
        
        self.console.print(Panel(info_text, border_style="green"))
        self.get_user_input()
        
        # TODO: Integrate with backend systems
        self.show_goodbye()
        return False  # Exit menu loop
    
    def run(self):
        """Main application loop."""
        try:
            while True:
                continue_menu = self.show_main_menu()
                
                if not continue_menu:
                    break
                    
                choice = input("\n> ").strip().upper()
                
                if choice == 'Q':
                    self.show_goodbye()
                    return 0
                elif choice == 'D':
                    dream_started = self.start_dream()
                    if not dream_started:
                        return 0
                elif choice == '1':
                    continue_menu = self.configure_prompt()
                elif choice == '2':
                    continue_menu = self.configure_aspect_ratio()
                elif choice == '3':
                    continue_menu = self.configure_frames()
                elif choice == '4':
                    continue_menu = self.configure_fps()
                elif choice == '5':
                    continue_menu = self.configure_quality()
                elif choice == '6':
                    continue_menu = self.configure_journey()
                else:
                    self.show_error("Invalid choice. Please try again.")
                    
        except KeyboardInterrupt:
            self.show_goodbye()
            return 0


def main():
    """Main entry point for ASCII Dream TUI."""
    try:
        app = ASCIIDreamTUI()
        return app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0


if __name__ == "__main__":
    main()