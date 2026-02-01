#!/usr/bin/env python3
"""
ASCII Dream - Beautiful TUI application with Textual.
"""
import sys
from typing import Optional

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical, Center
    from textual.widgets import Static, Button, Label, OptionList
    from textual.widgets.option_list import Option
    from textual.screen import Screen
    from textual import on
    from textual.binding import Binding

    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    print(f"Required library not available: {e}")
    print("Please install with: pip install textual")
    sys.exit(1)


# ASCII art title for ASCII DREAM
ASCII_TITLE = """ █████╗ ███████╗ ██████╗██╗██╗    ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗
██╔══██╗██╔════╝██╔════╝██║██║    ██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║
███████║███████╗██║     ██║██║    ██║  ██║██████╔╝█████╗  ███████║██╔████╔██║
██╔══██║╚════██║██║     ██║██║    ██║  ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║
██║  ██║███████║╚██████╗██║██║    ██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"""


class MainMenuScreen(Screen):
    """Main menu screen."""

    CSS = """
    MainMenuScreen {
        align: center middle;
        background: $background;
    }

    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
    }

    #tagline {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
        margin-bottom: 2;
    }

    #menu-container {
        width: auto;
        height: auto;
        align: center middle;
    }

    OptionList {
        width: 50;
        height: auto;
        background: $surface;
        border: none;
    }

    OptionList:focus {
        border: none;
    }

    OptionList > .option-list--option {
        background: transparent;
        color: $text;
    }

    OptionList > .option-list--option-highlighted {
        background: transparent;
        color: $warning;
        text-style: bold;
    }

    #controls {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("escape", "quit", "Quit", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the main menu."""
        yield Static(ASCII_TITLE, id="title")
        yield Static("Generate beautiful, evolving ASCII art from AI dreams", id="tagline")

        with Container(id="menu-container"):
            yield OptionList(
                Option("Start Dream", id="start"),
                Option("Configure Settings", id="settings"),
                Option("Quit", id="quit"),
            )

        yield Static("↑/↓: Navigate  •  Enter: Select  •  Q/Esc: Quit", id="controls")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle menu selection."""
        if event.option.id == "quit":
            self.app.exit()
        elif event.option.id == "settings":
            self.app.push_screen(SettingsScreen())
        elif event.option.id == "start":
            self.app.push_screen(DreamScreen())


class SettingsScreen(Screen):
    """Settings configuration screen."""

    CSS = """
    SettingsScreen {
        align: center middle;
        background: $background;
    }

    #settings-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    #settings-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }

    .setting-row {
        width: 100%;
        height: auto;
        color: $text;
    }

    .setting-label {
        color: $text-muted;
    }

    .setting-value {
        color: $accent;
    }

    #settings-instructions {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 1;
    }

    #settings-options {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin-top: 1;
        margin-bottom: 1;
    }

    #back-hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
        Binding("1", "config_prompt", "Prompt", show=False),
        Binding("2", "config_ratio", "Ratio", show=False),
        Binding("3", "config_frames", "Frames", show=False),
        Binding("4", "config_fps", "FPS", show=False),
        Binding("5", "config_quality", "Quality", show=False),
        Binding("6", "config_theme", "Theme", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        yield Static("⚙ Settings", id="settings-title")

        with Container(id="settings-box"):
            app = self.app
            if hasattr(app, 'config'):
                config = app.config
                yield Static("", classes="setting-row")
                yield Static(
                    f"[dim]Prompt:[/dim] [cyan]{config['prompt'] if config['prompt'] else '(journey mode)'}[/cyan]",
                    classes="setting-row"
                )
                yield Static(
                    f"[dim]Aspect Ratio:[/dim] [cyan]{config['aspect_ratio']}[/cyan]",
                    classes="setting-row"
                )
                yield Static(
                    f"[dim]Frame Count:[/dim] [cyan]{config['frames']}[/cyan]",
                    classes="setting-row"
                )
                yield Static(
                    f"[dim]Frame Rate:[/dim] [cyan]{config['fps']} fps[/cyan]",
                    classes="setting-row"
                )
                yield Static(
                    f"[dim]Quality:[/dim] [cyan]{'Fast' if config['fast'] else 'Normal'}[/cyan]",
                    classes="setting-row"
                )
                yield Static(
                    f"[dim]Journey Theme:[/dim] [cyan]{config['journey'].title()}[/cyan]",
                    classes="setting-row"
                )
                yield Static("", classes="setting-row")

        yield Static("Press 1-6 to configure options  •  Esc to go back", id="settings-instructions")
        yield Static("[yellow]1[/yellow][dim]:Prompt  [/dim][yellow]2[/yellow][dim]:Ratio  [/dim][yellow]3[/yellow][dim]:Frames  [/dim][yellow]4[/yellow][dim]:FPS  [/dim][yellow]5[/yellow][dim]:Quality  [/dim][yellow]6[/yellow][dim]:Theme[/dim]", id="settings-options")

    def action_config_prompt(self) -> None:
        """Configure prompt."""
        self.app.push_screen(ConfigPromptScreen())

    def action_config_ratio(self) -> None:
        """Configure aspect ratio."""
        self.app.push_screen(ConfigRatioScreen())

    def action_config_frames(self) -> None:
        """Configure frames."""
        self.app.push_screen(ConfigFramesScreen())

    def action_config_fps(self) -> None:
        """Configure FPS."""
        self.app.push_screen(ConfigFPSScreen())

    def action_config_quality(self) -> None:
        """Configure quality."""
        self.app.push_screen(ConfigQualityScreen())

    def action_config_theme(self) -> None:
        """Configure theme."""
        self.app.push_screen(ConfigThemeScreen())


class ConfigPromptScreen(Screen):
    """Prompt configuration screen."""

    CSS = """
    ConfigPromptScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 2;
    }

    #config-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose prompt config screen."""
        yield Static("Configure Prompt", id="config-title")
        with Container(id="config-box"):
            yield Static("\nNOTE: Interactive input not yet implemented in this Textual demo.\n", classes="setting-row")
            yield Static("Options: Type custom prompt or 'journey' for evolving themes\n", classes="setting-row")
        yield Static("Press Esc to go back", id="hint")


class ConfigRatioScreen(Screen):
    """Aspect ratio configuration screen."""

    CSS = """
    ConfigRatioScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 40;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose ratio config screen."""
        yield Static("Configure Aspect Ratio", id="config-title")

        current = self.app.config['aspect_ratio']
        options = ["1:1", "16:9", "9:16", "4:3", "3:4"]

        yield OptionList(
            *[Option(f"{r}{' ← CURRENT' if r == current else ''}", id=r) for r in options]
        )
        yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle ratio selection."""
        self.app.config['aspect_ratio'] = event.option.id
        self.app.pop_screen()


class ConfigFramesScreen(Screen):
    """Frame count configuration screen."""

    CSS = """
    ConfigFramesScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 2;
    }

    #config-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose frames config screen."""
        yield Static("Configure Frame Count", id="config-title")
        with Container(id="config-box"):
            current = self.app.config['frames']
            yield Static(f"\nCurrent: {current}", classes="setting-row")
            yield Static("\nNOTE: Interactive input not yet implemented.\n", classes="setting-row")
            yield Static("Range: 1-50 frames\n", classes="setting-row")
        yield Static("Press Esc to go back", id="hint")


class ConfigFPSScreen(Screen):
    """FPS configuration screen."""

    CSS = """
    ConfigFPSScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 2;
    }

    #config-box {
        width: 70;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose FPS config screen."""
        yield Static("Configure Frame Rate", id="config-title")
        with Container(id="config-box"):
            current = self.app.config['fps']
            yield Static(f"\nCurrent: {current} fps", classes="setting-row")
            yield Static("\nNOTE: Interactive input not yet implemented.\n", classes="setting-row")
            yield Static("Range: 0.5-5.0 fps\n", classes="setting-row")
        yield Static("Press Esc to go back", id="hint")


class ConfigQualityScreen(Screen):
    """Quality configuration screen."""

    CSS = """
    ConfigQualityScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose quality config screen."""
        yield Static("Configure Quality", id="config-title")

        current = "fast" if self.app.config['fast'] else "normal"

        yield OptionList(
            Option(f"Fast (256x256, quicker){' ← CURRENT' if current == 'fast' else ''}", id="fast"),
            Option(f"Normal (512x512, higher quality){' ← CURRENT' if current == 'normal' else ''}", id="normal"),
        )
        yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle quality selection."""
        self.app.config['fast'] = (event.option.id == "fast")
        self.app.pop_screen()


class ConfigThemeScreen(Screen):
    """Theme configuration screen."""

    CSS = """
    ConfigThemeScreen {
        align: center middle;
        background: $background;
    }

    #config-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    OptionList {
        width: 40;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose theme config screen."""
        yield Static("Configure Journey Theme", id="config-title")

        current = self.app.config['journey']
        themes = ["abstract", "nature", "cosmic", "liquid"]

        yield OptionList(
            *[Option(f"{t.title()}{' ← CURRENT' if t == current else ''}", id=t) for t in themes]
        )
        yield Static("↑/↓: Navigate  •  Enter: Select  •  Esc: Back", id="hint")

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle theme selection."""
        self.app.config['journey'] = event.option.id
        self.app.pop_screen()


class DreamScreen(Screen):
    """Dream generation screen (placeholder)."""

    CSS = """
    DreamScreen {
        align: center middle;
        background: $background;
    }

    #dream-box {
        width: 70;
        height: auto;
        border: solid $success;
        padding: 2 4;
        background: $surface;
    }

    .dream-row {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin: 1;
    }

    #hint {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "app.quit", "Quit", show=False),
        Binding("enter", "start_generation", "Start", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose dream screen."""
        with Container(id="dream-box"):
            yield Static("[bold green]Dream Configuration Ready![/bold green]", classes="dream-row")
            yield Static("", classes="dream-row")

            config = self.app.config
            yield Static(f"Prompt: {config['prompt'] if config['prompt'] else 'Journey Mode'}", classes="dream-row")
            yield Static(f"Aspect Ratio: {config['aspect_ratio']}", classes="dream-row")
            yield Static(f"Frames: {config['frames']}", classes="dream-row")
            yield Static(f"Quality: {'Fast' if config['fast'] else 'Normal'}", classes="dream-row")
            yield Static(f"FPS: {config['fps']}", classes="dream-row")
            yield Static("", classes="dream-row")
            yield Static("[dim]Press Enter to start generation (placeholder)[/dim]", classes="dream-row")

        yield Static("Enter: Start  •  Esc: Back  •  Q: Quit", id="hint")

    def action_start_generation(self) -> None:
        """Start generation (placeholder)."""
        # TODO: Integrate with backend
        self.app.exit(message="Dream generation would start here!")


class ASCIIDreamApp(App):
    """ASCII Dream TUI application."""

    CSS = """
    Screen {
        background: $background;
    }
    """

    # Define color scheme similar to p2pong
    COLORS = {
        "background": "#000000",
        "surface": "#141414",
        "primary": "#00ffff",
        "accent": "#00ffff",
        "success": "#00ff00",
        "warning": "#ffff00",
        "error": "#ff0000",
        "text": "#ffffff",
        "text-muted": "#666666",
    }

    def __init__(self):
        super().__init__()
        self.config = {
            'prompt': '',
            'aspect_ratio': '1:1',
            'frames': 3,
            'fast': False,
            'fps': 2.0,
            'journey': 'abstract',
            'custom_prompt': False
        }

    def on_mount(self) -> None:
        """Initialize the app."""
        self.push_screen(MainMenuScreen())


def main():
    """Main entry point for ASCII Dream TUI."""
    app = ASCIIDreamApp()
    result = app.run()
    if result:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
