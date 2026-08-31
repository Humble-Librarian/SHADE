# ==============================================================================
# Script 4: ecb_vs_cbc_image.py
# Purpose: Visually demonstrate pattern leakage in ECB vs CBC block cipher modes
# ==============================================================================

# IMPORTS
from PIL import Image, ImageDraw
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# STEP 1 — Prepare the image
img = Image.new("RGB", (256, 256), "white")
draw = ImageDraw.Draw(img)
draw.rectangle([50, 50, 200, 200], fill="blue")   # Solid blue rectangle on white background
img.save("sample.bmp")
print("Generated original test image: sample.bmp (256x256 BMP)")

# STEP 2 — Read header and pixel data separately
with open("sample.bmp", "rb") as f:
    header = f.read(54)       # First 54 bytes = standard Windows BMP header
    pixel_data = f.read()     # Remaining bytes = raw RGB pixel data

# STEP 3 — Encrypt pixels with ECB
key = get_random_bytes(16)

cipher_ecb = AES.new(key, AES.MODE_ECB)     # No IV needed for ECB
padded = pad(pixel_data, 16)
ecb_encrypted = cipher_ecb.encrypt(padded)[:len(pixel_data)]  # Trim back to original payload length

with open("ecb_output.bmp", "wb") as f:
    f.write(header + ecb_encrypted)

print("Generated ECB encrypted image: ecb_output.bmp")

# STEP 4 — Encrypt pixels with CBC
iv = get_random_bytes(16)
cipher_cbc = AES.new(key, AES.MODE_CBC, iv)
cbc_encrypted = cipher_cbc.encrypt(padded)[:len(pixel_data)]  # Trim back to original payload length

with open("cbc_output.bmp", "wb") as f:
    f.write(header + cbc_encrypted)

print("Generated CBC encrypted image: cbc_output.bmp")

# STEP 5 — Summary
print("\n--- Visual Pattern Leakage Summary ---")
print("1. sample.bmp      -> Original image with clear blue rectangle")
print("2. ecb_output.bmp  -> ECB Mode: Identical plaintext blocks produce identical ciphertext blocks;")
print("                      the outline/shape of the rectangle remains clearly visible.")
print("3. cbc_output.bmp  -> CBC Mode: Chaining mechanism (XOR with previous block) ensures identical")
print("                      plaintext blocks produce pseudo-random noise with no visible pattern.")
