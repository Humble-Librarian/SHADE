# ==============================================================================
# Script 2: des_encrypt.py
# Purpose: 3-DES (Triple DES) CBC Encryption, Decryption, Verification, and Timing
# ==============================================================================

# IMPORTS
from Crypto.Cipher import DES3
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

# STEP 1 — Generate Key and IV (3-DES parameters)
key = get_random_bytes(24)    # 24 bytes for 3-DES (Triple-length key)
iv  = get_random_bytes(8)     # 8 bytes IV (DES block size is 8 bytes)

# STEP 2 — Read the plaintext file
with open("patient_report.txt", "rb") as f:
    plaintext = f.read()

# STEP 3 — Encrypt
cipher = DES3.new(key, DES3.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(plaintext, 8))    # Block size is 8 bytes

with open("patient_report_3DES_encrypted.bin", "wb") as f:
    f.write(ciphertext)

print(f"Encrypted patient_report.txt -> patient_report_3DES_encrypted.bin ({len(ciphertext)} bytes)")

# STEP 4 — Decrypt
cipher_dec = DES3.new(key, DES3.MODE_CBC, iv)
decrypted = unpad(cipher_dec.decrypt(ciphertext), 8)

with open("patient_report_3DES_decrypted.txt", "wb") as f:
    f.write(decrypted)

print("Decrypted patient_report_3DES_encrypted.bin -> patient_report_3DES_decrypted.txt")

# STEP 5 — Verify
if plaintext == decrypted:
    print("✅ 3-DES Decryption Successful — file matches original")
else:
    print("❌ Mismatch!")

# STEP 6 — Timing (run this for all 3 file sizes)
print("\n--- 3-DES Encryption Timing Benchmarks ---")
for filename in ["test_1kb.txt", "test_100kb.txt", "test_1mb.txt"]:
    with open(filename, "rb") as f:
        file_data = f.read()
    start = time.time()
    bench_cipher = DES3.new(key, DES3.MODE_CBC, iv)
    _ = bench_cipher.encrypt(pad(file_data, 8))
    end = time.time()
    print(f"{filename}: 3-DES encryption took {(end - start) * 1000:.4f} ms")
