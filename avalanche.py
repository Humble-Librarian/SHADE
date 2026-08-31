# ==============================================================================
# Script 3: avalanche.py
# Purpose: Measure the Avalanche Effect in AES-128 (Flipping 1 bit in plaintext)
# ==============================================================================

# IMPORTS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# STEP 1 — Prepare two plaintexts
with open("patient_report.txt", "rb") as f:
    original = f.read()

modified = bytearray(original)
modified[0] ^= 0x01      # Flip the last bit of the first byte
modified = bytes(modified)

print("Original byte 0:", bin(original[0]))
print("Modified byte 0:", bin(modified[0]))

# STEP 2 — Encrypt both with SAME key and IV
if not os.path.exists("key.bin") or not os.path.exists("iv.bin"):
    raise FileNotFoundError("key.bin and/or iv.bin not found. Run aes_encrypt.py first.")

with open("key.bin", "rb") as f:
    key = f.read()

with open("iv.bin", "rb") as f:
    iv = f.read()

cipher1 = AES.new(key, AES.MODE_CBC, iv)
ct1 = cipher1.encrypt(pad(original, 16))

cipher2 = AES.new(key, AES.MODE_CBC, iv)
ct2 = cipher2.encrypt(pad(modified, 16))

# STEP 3 — Compare bit by bit
length = min(len(ct1), len(ct2))
diff_bits = 0
total_bits = length * 8

for i in range(length):
    xor_byte = ct1[i] ^ ct2[i]          # XOR yields 1 at every differing bit position
    diff_bits += bin(xor_byte).count('1')  # Count the 1s

# STEP 4 — Print result
percentage = (diff_bits / total_bits) * 100
print("\n--- Avalanche Effect Results ---")
print(f"Total bits compared: {total_bits}")
print(f"Bits changed: {diff_bits} / {total_bits}")
print(f"Avalanche Effect: {percentage:.2f}%")

if 45.0 <= percentage <= 55.0:
    print("✅ Excellent Avalanche Effect (Optimal cryptographic range: 45% - 55%)")
else:
    print("ℹ️ Avalanche effect observed.")
