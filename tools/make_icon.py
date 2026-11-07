# -*- coding: utf-8 -*-
"""Generate the app icon (PNG + PNG-compressed ICO) without extra libraries."""

import os
import struct

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "web", "assets")
os.makedirs(OUT, exist_ok=True)

size = 256
image = np.full((size, size, 3), (12, 9, 6), np.uint8)
# subtle vignette
yy, xx = np.mgrid[0:size, 0:size]
d = np.sqrt((xx - 128) ** 2 + (yy - 128) ** 2)
glow = np.clip(1.0 - d / 190.0, 0, 1) ** 2
image = np.clip(image.astype(np.float32) + glow[:, :, None] * np.array([24, 48, 40]), 0, 255).astype(np.uint8)

teal = (212, 234, 94)
lime = (100, 242, 190)
cv2.ellipse(image, (128, 128), (86, 50), 0, 0, 360, teal, 5, cv2.LINE_AA)
cv2.ellipse(image, (128, 128), (58, 33), 0, 0, 360, teal, 2, cv2.LINE_AA)
cv2.circle(image, (128, 128), 25, teal, 4, cv2.LINE_AA)
cv2.circle(image, (128, 128), 13, lime, -1, cv2.LINE_AA)
cv2.circle(image, (134, 122), 4, (12, 9, 6), -1, cv2.LINE_AA)
for x, y, dx, dy in ((28, 28, 1, 1), (228, 28, -1, 1), (28, 228, 1, -1), (228, 228, -1, -1)):
    cv2.line(image, (x, y), (x + 22 * dx, y), teal, 3, cv2.LINE_AA)
    cv2.line(image, (x, y), (x, y + 22 * dy), teal, 3, cv2.LINE_AA)

png_path = os.path.join(OUT, "logo.png")
cv2.imwrite(png_path, image)
with open(png_path, "rb") as handle:
    png = handle.read()

# PNG-compressed ICO with one 256x256 entry.
header = struct.pack("<HHH", 0, 1, 1)
entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(png), 22)
ico_path = os.path.join(OUT, "logo.ico")
with open(ico_path, "wb") as handle:
    handle.write(header + entry + png)
print("wrote", png_path, len(png))
print("wrote", ico_path, 22 + len(png))
