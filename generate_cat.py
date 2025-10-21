#!/usr/bin/env python3
from PIL import Image
import numpy as np
import time
import os

# Path to today's cat
IMG_PATH = "/home/upbiology/kitty/output/cat.png"
FB_PATH = "/dev/fb1"

# Ensure the image exists
if not os.path.exists(IMG_PATH):
    print(f"❌ No cat image found at {IMG_PATH}")
    raise SystemExit

# Load and resize image
print("🐾 Drawing cat to TFT framebuffer...")
img = Image.open(IMG_PATH).resize((480, 320))
arr = np.array(img.convert("RGB"), dtype=np.uint16)

# Convert to RGB565 (16-bit)
r = ((arr[:, :, 0] >> 3) & 0x1F) << 11
g = ((arr[:, :, 1] >> 2) & 0x3F) << 5
b = (arr[:, :, 2] >> 3) & 0x1F
rgb565 = (r | g | b).flatten().astype(np.uint16).tobytes()

# Write directly to framebuffer
with open(FB_PATH, "wb") as f:
    f.write(rgb565)

print("✅ Cat displayed successfully!")
print("🕒 Holding image... (Ctrl+C to exit)")
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    print("\n👋 Exiting and clearing screen...")
    blank = np.zeros((320, 480, 3), dtype=np.uint8)
    arr = np.array(Image.fromarray(blank).convert("RGB"), dtype=np.uint16)
    r = ((arr[:, :, 0] >> 3) & 0x1F) << 11
    g = ((arr[:, :, 1] >> 2) & 0x3F) << 5
    b = (arr[:, :, 2] >> 3) & 0x1F
    rgb565 = (r | g | b).flatten().astype(np.uint16).tobytes()
    with open(FB_PATH, "wb") as f:
        f.write(rgb565)
