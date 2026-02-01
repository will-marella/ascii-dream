"""
Modal Cold Start Benchmark for ASCII Dream
Tests actual cold start and warm invocation times with SD-Turbo
"""

import modal
import time

# Create Modal app
app = modal.App("ascii-dream-benchmark")

# Define image with dependencies
image = modal.Image.debian_slim().pip_install(
    "diffusers==0.31.0",
    "transformers==4.46.0",
    "accelerate==1.2.1",
    "torch==2.5.1",
    "huggingface_hub==0.26.5",
)


@app.function(
    image=image,
    gpu="t4",  # Cheapest GPU option (lowercase per Modal convention)
    timeout=300,
)
def generate_image(prompt: str = "abstract colorful shapes"):
    """Generate a single image with SD-Turbo"""
    from diffusers import AutoPipelineForText2Image
    import torch

    start = time.time()

    # Load model (this is cached after first run)
    print("Loading model...")
    load_start = time.time()
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float16,
        variant="fp16"
    )
    pipe = pipe.to("cuda")
    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.2f}s")

    # Generate image
    print("Generating image...")
    gen_start = time.time()
    image = pipe(
        prompt=prompt,
        num_inference_steps=1,  # SD-Turbo optimized for 1 step
        guidance_scale=0.0,
        height=512,
        width=512,
    ).images[0]
    gen_time = time.time() - gen_start
    print(f"Image generated in {gen_time:.2f}s")

    total_time = time.time() - start

    return {
        "load_time": load_time,
        "generation_time": gen_time,
        "total_time": total_time,
        "image_size": (512, 512),
    }


@app.local_entrypoint()
def main():
    """Run benchmark tests"""

    print("=" * 60)
    print("ASCII DREAM - Modal Cold Start Benchmark")
    print("=" * 60)

    # Test 1: Cold start
    print("\n[TEST 1] Cold Start (first invocation)")
    print("-" * 60)
    client_start = time.time()
    result1 = generate_image.remote("abstract geometric patterns")
    client_total = time.time() - client_start

    print(f"\nResults:")
    print(f"  Model Load Time:    {result1['load_time']:.2f}s")
    print(f"  Generation Time:    {result1['generation_time']:.2f}s")
    print(f"  Function Total:     {result1['total_time']:.2f}s")
    print(f"  Client Total:       {client_total:.2f}s (includes network)")
    print(f"  Cold Start Penalty: {client_total - result1['total_time']:.2f}s")

    # Test 2: Warm invocation (immediate)
    print("\n[TEST 2] Warm Invocation (immediate)")
    print("-" * 60)
    client_start = time.time()
    result2 = generate_image.remote("flowing colorful shapes")
    client_total = time.time() - client_start

    print(f"\nResults:")
    print(f"  Model Load Time:    {result2['load_time']:.2f}s")
    print(f"  Generation Time:    {result2['generation_time']:.2f}s")
    print(f"  Function Total:     {result2['total_time']:.2f}s")
    print(f"  Client Total:       {client_total:.2f}s")

    # Test 3: Multiple rapid invocations
    print("\n[TEST 3] Batch of 5 rapid invocations")
    print("-" * 60)
    prompts = [
        "abstract waves",
        "geometric shapes",
        "organic patterns",
        "swirling colors",
        "fluid motion",
    ]

    batch_start = time.time()
    times = []
    for i, prompt in enumerate(prompts, 1):
        start = time.time()
        result = generate_image.remote(prompt)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Image {i}: {elapsed:.2f}s (gen: {result['generation_time']:.2f}s)")

    batch_total = time.time() - batch_start
    avg_time = sum(times) / len(times)

    print(f"\nBatch Summary:")
    print(f"  Total Time:    {batch_total:.2f}s")
    print(f"  Average Time:  {avg_time:.2f}s per image")
    print(f"  Min Time:      {min(times):.2f}s")
    print(f"  Max Time:      {max(times):.2f}s")

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS FOR ASCII DREAM")
    print("=" * 60)

    sustainable_rate = 1 / avg_time
    print(f"\nSustainable Generation Rate: {sustainable_rate:.2f} images/second")
    print(f"Time per frame (avg):        {avg_time:.2f}s")

    if avg_time <= 3:
        print("\n✓ Can sustain 3-5s refresh rate comfortably")
    elif avg_time <= 5:
        print("\n⚠ Can sustain 5s refresh rate, 3s might be tight")
    else:
        print("\n✗ May struggle with 5s refresh rate")

    queue_depth = int(avg_time / 3) + 2  # Buffer for safety
    print(f"\nRecommended Queue Depth:     {queue_depth} images")
    print(f"  (Generate {queue_depth} ahead to hide latency)")

    print("\n" + "=" * 60)
