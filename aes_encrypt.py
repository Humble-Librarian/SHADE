# ==============================================================================
# Script 1: aes_encrypt.py
# Purpose: AES-128 CBC Encryption, Decryption, Verification, and Performance Timing
# ==============================================================================

# IMPORTS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import time
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# STEP 1 — Generate Key and IV
key = get_random_bytes(16)      # 16 bytes = 128-bit AES key
iv  = get_random_bytes(16)      # 16 bytes IV for CBC mode

# Save both to files
with open("key.bin", "wb") as f:
    f.write(key)

with open("iv.bin", "wb") as f:
    f.write(iv)

print("Generated and saved key.bin (16 bytes) and iv.bin (16 bytes).")

# STEP 2 — Read the plaintext file
with open("patient_report.txt", "rb") as f:
    plaintext = f.read()

# STEP 3 — Encrypt
cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(plaintext, 16))

with open("patient_report_AES_encrypted.bin", "wb") as f:
    f.write(ciphertext)

print(f"Encrypted patient_report.txt -> patient_report_AES_encrypted.bin ({len(ciphertext)} bytes)")

# STEP 4 — Decrypt
cipher_dec = AES.new(key, AES.MODE_CBC, iv)
decrypted = unpad(cipher_dec.decrypt(ciphertext), 16)

with open("patient_report_AES_decrypted.txt", "wb") as f:
    f.write(decrypted)

print("Decrypted patient_report_AES_encrypted.bin -> patient_report_AES_decrypted.txt")

# STEP 5 — Verify
if plaintext == decrypted:
    print("✅ AES Decryption Successful — file matches original")
else:
    print("❌ Mismatch!")

# STEP 6 — Timing (run this for all 3 file sizes)
print("\n--- AES Encryption Timing Benchmarks ---")
for filename in ["test_1kb.txt", "test_100kb.txt", "test_1mb.txt"]:
    with open(filename, "rb") as f:
        file_data = f.read()
    start = time.time()
    bench_cipher = AES.new(key, AES.MODE_CBC, iv)
    _ = bench_cipher.encrypt(pad(file_data, 16))
    end = time.time()
    print(f"{filename}: AES encryption took {(end - start) * 1000:.4f} ms")
