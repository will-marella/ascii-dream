"""
Modal backend for SD-Turbo image generation with model caching.
"""
import modal
import io
import os
import warnings
from PIL import Image

# Suppress warnings for clean output
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
warnings.filterwarnings("ignore")

# Create Modal app
app = modal.App("ascii-dream")

# Define container image with dependencies
image = modal.Image.debian_slim().pip_install(
    "diffusers==0.31.0",
    "transformers==4.46.0",
    "accelerate==1.2.1",
    "torch==2.5.1",
    "huggingface_hub==0.26.5",
    "pillow",
)


@app.cls(
    image=image,
    gpu="t4",  # Cheapest GPU option
    timeout=300,
    min_containers=1,  # Keep 1 container warm for instant response
    scaledown_window=180,  # Keep alive 3 mins between calls
)
class ImageGenerator:
    """Class-based Modal function with model caching."""

    @modal.enter()
    def load_model(self):
        """Load SD-Turbo model once when container starts."""
        from diffusers import AutoPipelineForText2Image
        from diffusers.utils import logging as diffusers_logging
        import torch

        # Disable diffusers progress bars and logging
        diffusers_logging.set_verbosity_error()

        # Load model (silent - output suppressed for clean UI)
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sd-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        self.pipe = self.pipe.to("cuda")

        # Disable progress bar for generation
        self.pipe.set_progress_bar_config(disable=True)

    @modal.method()
    def generate(self, prompt: str, height: int = 512, width: int = 512, seed: int | None = None) -> bytes:
        """
        Generate image from prompt. Model is already loaded.

        Args:
            prompt: Text prompt for generation
            height: Image height in pixels
            width: Image width in pixels  
            seed: Random seed for noise consistency (None = random)

        Returns:
            PNG image as bytes for efficient network transfer
        """
        # Set seed for consistent noise if provided
        if seed is not None:
            import torch
            generator = torch.Generator().manual_seed(seed)
        else:
            generator = None

        image = self.pipe(
            prompt=prompt,
            num_inference_steps=1,
            guidance_scale=0.0,
            height=height,
            width=width,
            generator=generator,
        ).images[0]

        # Serialize to bytes
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()


# Helper function to get generator reference
def get_generator():
    """Get reference to ImageGenerator class for use in Modal app context."""
    return ImageGenerator()
