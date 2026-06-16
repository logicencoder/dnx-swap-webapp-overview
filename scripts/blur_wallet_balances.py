#!/usr/bin/env python3
"""Anonymize wallet balance strip on public overview hero image."""
from PIL import Image, ImageFilter

path = "/home/lojzo/dex-swapper-overview/assets/dex-swapper-featured.png"
img = Image.open(path).convert("RGB")
w, h = img.size
box = (int(w * 0.38), int(h * 0.055), int(w * 0.98), int(h * 0.19))
crop = img.crop(box)
img.paste(crop.filter(ImageFilter.GaussianBlur(radius=14)), box)
img.save(path, optimize=True)
print(f"blurred {path} box={box}")
