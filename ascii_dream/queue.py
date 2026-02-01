"""
Async queue management for prefetching generated images.
"""
import asyncio
from typing import Iterator
from PIL import Image


class ImageQueue:
    """Manages prefetching queue for generated images."""

    def __init__(
        self,
        generator,
        prompt_iterator: Iterator[str] | Iterator[tuple],
        queue_depth: int = 2,
        image_size: tuple[int, int] = (512, 512),
        frames_per_cycle: int = 1,
    ):
        """
        Initialize image queue.

        Args:
            generator: ModalClient instance
            prompt_iterator: Iterator yielding prompts
            queue_depth: Number of images to prefetch
            image_size: (width, height) for generation
            frames_per_cycle: Number of frames to cycle through
        """
        self.generator = generator
        self.prompt_iterator = prompt_iterator
        self.queue_depth = queue_depth
        self.image_size = image_size
        self.frames_per_cycle = frames_per_cycle
        self.queue = asyncio.Queue(maxsize=queue_depth)
        self._producer_task = None
        self._running = False
        self._frame_index = 0

    async def _generate_with_retry(
        self, prompt: str, seed: int | None = None, max_retries: int = 2
    ) -> tuple[str, Image.Image]:
        """
        Generate image with retry logic.

        Args:
            prompt: Text prompt for generation
            seed: Seed for noise consistency
            max_retries: Number of retry attempts

        Returns:
            (prompt, PIL Image)
        """
        for attempt in range(max_retries):
            try:
                image = await self.generator.generate(
                    prompt, height=self.image_size[1], width=self.image_size[0], seed=seed
                )
                return (prompt, image)

            except Exception as e:
                if attempt == max_retries - 1:
                    # Final fallback prompt (silent - don't clutter output)
                    image = await self.generator.generate(
                        "abstract colorful shapes",
                        height=self.image_size[1],
                        width=self.image_size[0],
                        seed=None,  # Use random seed for fallback
                    )
                    return ("abstract colorful shapes [fallback]", image)

                # Exponential backoff
                await asyncio.sleep(2**attempt)

    async def _producer(self):
        """Producer task: continuously generate and queue images."""
        prompt_buffer = []
        cycle_count = 0
        
        while self._running:
            try:
                # Check if we need to refresh prompt buffer (new cycle)
                if cycle_count == 0 or self.frames_per_cycle > 1:
                    # Clear buffer and build new prompt list
                    prompt_buffer = []
                    for i in range(self.frames_per_cycle):
                        try:
                            prompt = next(self.prompt_iterator)
                            prompt_buffer.append(prompt)
                        except StopIteration:
                            # Use fallback prompt for remaining slots
                            prompt_buffer.append("abstract colorful patterns")
                            break
                
                    prompt_buffer = prompt_buffer[:self.frames_per_cycle]
                    cycle_count += 1
                
                # Get current frame prompt
                prompt = prompt_buffer[self._frame_index % len(prompt_buffer)]
                
                # Generate image
                image = await self._generate_with_retry(prompt)
                
                # Put in queue (just the image)
                await self.queue.put(image)
                
                # Move to next frame
                self._frame_index = (self._frame_index + 1) % len(prompt_buffer)

            except StopIteration:
                # Prompt iterator exhausted (shouldn't happen with infinite iterator)
                break
            except Exception as e:
                # Silent retry - don't clutter output
                await asyncio.sleep(1)

    def start(self):
        """Start producer task."""
        self._running = True
        self._producer_task = asyncio.create_task(self._producer())

    async def stop(self):
        """Stop producer task gracefully."""
        self._running = False
        if self._producer_task:
            await self._producer_task

    async def get(self) -> tuple[str, Image.Image]:
        """
        Get next image from queue.

        Returns:
            (prompt, PIL Image)
        """
        return await self.queue.get()

    def empty(self) -> bool:
        """Check if queue is empty."""
        return self.queue.empty()

    async def prefill(self):
        """Wait for queue to fill to target depth (for startup)."""
        while self.queue.qsize() < self.queue_depth:
            await asyncio.sleep(0.1)
