<p align="center">
  <img src="assets/ascii-dream-tui.png" alt="ASCII Dream" width="800">
</p>

<p align="center">
  <img src="assets/demo.gif" alt="ASCII Dream Demo" width="900">
</p>

## ✨ Quick Start

```bash
# Install from GitHub
pip install git+https://github.com/will-marella/ascii-dream.git

# Authenticate with Modal (one-time setup)
modal setup

# Run it!
ascii-dream
```

That's it! First run downloads the AI model (~2GB, one-time only).

## 🎨 Features

- **AI-Powered Generation** – Uses Stability AI's SD-Turbo model for instant image creation
- **Real-Time ASCII Rendering** – Converts images to beautiful colored ASCII art with proper terminal color support
- **Interactive TUI** – Simple, beautiful menu interface
- **Infinite Dreams** – Continuously generates unique art at 1 FPS
- **Journey Modes** – Auto-evolving prompts that take you through themed visual journeys (abstract, nature, cosmic, liquid)

## 📋 Requirements

- Python 3.8+
- [Modal](https://modal.com) account (free) – Provides GPU access for AI generation

## 🎮 Usage

Simply run:

```bash
ascii-dream
```

**Controls:**
- **Enter** – Start dreaming
- **Space** – Pause/resume
- **Esc** – Go back
- **Q** – Quit

## How It Works

```
┌──────────────────────────────────────────────────────┐
│  ASCII Dream TUI                                     │
└─────────────────┬──────────────────────────────────┘
                  │
      ┌───────────┴────────────┐
      │                        │
      ▼                        ▼
[Settings Menu]         [Dream Generation]
      │                        │
      └───────────┬────────────┘
                  │
      ┌───────────▼──────────────┐
      │  Generate Prompt         │
      │  (or use journey mode)   │
      └───────────┬──────────────┘
                  │
      ┌───────────▼──────────────────┐
      │  AI Image Generation         │
      │  (Stability SD-Turbo on GPU) │
      └───────────┬──────────────────┘
                  │
      ┌───────────▼──────────────┐
      │  Convert to ASCII Art     │
      │  (With colors)           │
      └───────────┬──────────────┘
                  │
      ┌───────────▼──────────────┐
      │  Real-Time Terminal      │
      │  Display (Live)          │
      └──────────────────────────┘
```

### Key Components

- **Modal Backend** – Runs AI inference on GPU in the cloud (Modal manages infrastructure)
- **Prompt Evolution** – Intelligently varies prompts using templates with random color/element substitution
- **Image Queue** – Async producer-consumer that prefetches images while current ones display
- **ASCII Converter** – Transforms PIL images to colored ASCII art with smart width detection
- **TUI (Textual)** – Full interactive menu system with real-time generation display

## Examples

### Default Journey Mode (Auto-Evolving)
```bash
ascii-dream
# Navigate: Start Dream → auto-generates abstract → nature → cosmic → liquid themes
```

### Custom Theme Journey
```bash
ascii-dream
# Go to Settings → Configure → Journey Theme → Select "nature"
# Start Dream → nature-themed evolution
```

### Multiple Frames (Animation)
```bash
ascii-dream
# Settings → Frames: 4 → Quality: Fast → Start Dream
# Generates 4 images, cycles through them
```

### High Quality (Slower)
```bash
ascii-dream
# Settings → Quality: Normal → Frames: 1 → Start Dream
# Single high-quality 512×512 image
```

## Architecture

### Project Structure

```
ascii-dream/
├── pyproject.toml              # Package configuration
├── README.md                   # This file
├── requirements.txt            # Legacy (use pyproject.toml)
│
├── ascii_dream/
│   ├── __init__.py            # Package metadata
│   ├── __main__.py            # TUI entry point
│   ├── tui_app.py             # Textual TUI implementation
│   ├── queue.py               # Image prefetching queue
│   │
│   ├── cli/
│   │   └── main.py            # CLI implementation (legacy)
│   │
│   ├── generation/
│   │   ├── modal_backend.py    # SD-Turbo GPU inference
│   │   ├── prompt_evolution.py # Prompt variation engine
│   │   └── dream_frames.py     # Frame correlation (unused currently)
│   │
│   └── rendering/
│       ├── ascii_converter.py  # Image → ASCII art
│       └── terminal_display.py # Terminal output management
```

### Technology Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| **GPU Inference** | Modal + Diffusers | AI image generation |
| **Image Model** | Stability AI SD-Turbo | 1-step diffusion (fast) |
| **Image Processing** | Pillow (PIL) | Image manipulation |
| **ASCII Conversion** | ascii-magic | Image → colored ASCII |
| **Terminal UI** | Textual | Interactive menu & display |
| **Terminal Output** | Rich | Styled terminal rendering |

## First Run Experience

The first run takes ~50 seconds because:
1. Modal downloads the SD-Turbo model (~2GB)
2. GPU container initializes on first call
3. Model is cached for subsequent runs

**Subsequent runs are much faster (~5-10s per image)** once the model is cached.

## Keyboard Controls

### In TUI Menu
- **↑/↓** – Navigate menu options
- **Enter** – Select option
- **Q/Esc** – Quit or go back

### During Dream Generation
- **Q** – Stop generation and return to menu
- **Esc** – Stop generation and return to menu

## Troubleshooting

### "Modal token not found"
Run:
```bash
modal token new
```
Follow the browser authentication flow to create your token.

### "No GPU available"
Modal may scale down your GPU during inactivity. Just try again – it will warm up a new container automatically.

### Slow generation on first run
This is expected! The model is being downloaded and the GPU container initialized. Subsequent runs will be significantly faster.

### Command not found: ascii-dream
Make sure you installed the package in editable mode:
```bash
pip install -e .
```

Then verify the installation:
```bash
which ascii-dream
```

## Performance Tips

- **Fast Mode**: Use `--fast` equivalent in settings for 256×256 images (2-3x faster)
- **Multiple Frames**: Generate 3-5 frames to create smooth animations
- **Journey Mode**: Auto-evolving themes are usually more interesting than static prompts

## Contributing

Interested in improving ASCII Dream? Here are some ideas:

- **Interactive Prompt Input** – ConfigPromptScreen has a placeholder ready for text input
- **More Journey Themes** – Add custom prompt templates for new themes
- **Better Color Mapping** – Improve ASCII character → color correlation
- **Performance Optimization** – Speed up ASCII conversion for large terminal widths
- **Export to File** – Save generated ASCII art as text/HTML/PNG

Feel free to open issues or submit pull requests!

## License

MIT License – See LICENSE file for details.

## Links

- **GitHub**: https://github.com/will-marella/ascii-dream
- **Modal**: https://modal.com (GPU inference platform)
- **Stable Diffusion**: https://huggingface.co/stabilityai/sd-turbo
- **Textual**: https://textual.textualize.io (TUI framework)

---

Enjoy your ASCII dreams! 🎨✨
