import time
import io
from PIL import Image, ImageOps
import sys
import os

# Add current dir to path to import models
sys.path.insert(0, os.getcwd())
from models.modeling_deepseekocr import load_image, load_pil_images

def benchmark_optimizations():
    print("--- ⚡ Bolt Optimization Benchmark ⚡ ---")

    # 1. Benchmark load_image (EXIF optimization)
    # Create a large image without EXIF
    img_no_exif = Image.new('RGB', (4000, 4000), color='white')

    start = time.time()
    for _ in range(50):
        _ = load_image(img_no_exif)
    elapsed_new = time.time() - start

    # Estimate old time based on measurement (ImageOps.exif_transpose always copies if no EXIF)
    start = time.time()
    for _ in range(50):
        _ = ImageOps.exif_transpose(img_no_exif)
    elapsed_old = time.time() - start

    print(f"load_image (no EXIF) - Old: {elapsed_old:.4f}s, New: {elapsed_new:.4f}s")
    print(f"Speedup: {elapsed_old/elapsed_new:.1f}x" if elapsed_new > 0 else "Speedup: Inf")

    # 2. Benchmark load_pil_images (Conditional RGB optimization)
    conv = [{
        "role": "User",
        "content": "<image>",
        "images": [img_no_exif]
    }]

    start = time.time()
    for _ in range(50):
        _ = load_pil_images(conv)
    elapsed_new_conv = time.time() - start

    # Simulate old behavior (unconditional convert)
    start = time.time()
    for _ in range(50):
        # mock load_image + unconditional convert
        img = ImageOps.exif_transpose(img_no_exif)
        _ = img.convert("RGB")
    elapsed_old_conv = time.time() - start

    print(f"load_pil_images (RGB input) - Old: {elapsed_old_conv:.4f}s, New: {elapsed_new_conv:.4f}s")
    print(f"Speedup: {elapsed_old_conv/elapsed_new_conv:.1f}x" if elapsed_new_conv > 0 else "Speedup: Inf")

    # 3. Benchmark Image Copy Delay (Memory/Time)
    start = time.time()
    for _ in range(50):
        # Simulate original infer() start
        _ = img_no_exif.copy()
    elapsed_copy = time.time() - start
    print(f"Delayed copy saving per 50 pages: {elapsed_copy:.4f}s")

if __name__ == "__main__":
    benchmark_optimizations()
