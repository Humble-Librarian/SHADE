# ==============================================================================
# Script 2 (Task C): tamper_detection.py
# Purpose: Simulate Active Ciphertext Tampering and Prove SHA-256 Detects Corrupted Data
# ==============================================================================

from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def find_file(filename):
    if os.path.exists(filename):
        return filename
    parent_path = os.path.join("..", filename)
    if os.path.exists(parent_path):
        return parent_path
    task_b_path = os.path.join("..", "task_b", filename)
    if os.path.exists(task_b_path):
        return task_b_path
    raise FileNotFoundError(f"Could not find required file: '{filename}'")

def compute_hash(data_or_path):
    if isinstance(data_or_path, (bytes, bytearray)):
        data = data_or_path
    else:
        with open(data_or_path, "rb") as f:
            data = f.read()
    h = SHA256.new(data)
    return h.hexdigest()

print("================================================================================")
print("             ACTIVE ATTACK SIMULATION — CIPHERTEXT TAMPERING                    ")
print("================================================================================")

# STEP 1 — Load the encrypted file and keys
cipher_path = find_file("patient_report_AES_encrypted.bin")
key_path = find_file("key.bin")
iv_path = find_file("iv.bin")
orig_hash_path = find_file("original_hash.txt")

with open(cipher_path, "rb") as f:
    ciphertext = f.read()

with open(key_path, "rb") as f:
    key = f.read()

with open(iv_path, "rb") as f:
    iv = f.read()

with open(orig_hash_path, "r", encoding="utf-8") as f:
    hash_original = f.read().strip()

print(f"Loaded original ciphertext ({len(ciphertext)} bytes) from: {cipher_path}")
print(f"Original Expected SHA-256 Hash: {hash_original}")

# STEP 2 — Simulate tampering (attacker flips bytes in transit)
tampered = bytearray(ciphertext)
tampered[10] ^= 0xFF     # Corrupt byte 10
tampered[50] ^= 0xAA     # Corrupt byte 50
tampered = bytes(tampered)

with open("patient_report_TAMPERED.bin", "wb") as f:
    f.write(tampered)

print("\n⚠️ Attack in Progress:")
print("   - Flipped bits at ciphertext byte index 10 (XOR 0xFF)")
print("   - Flipped bits at ciphertext byte index 50 (XOR 0xAA)")
print("   - Saved corrupted payload -> patient_report_TAMPERED.bin")

# STEP 3 — Receiver decrypts the tampered file
print("\n================================================================================")
print("                   RECEIVER ATTEMPTS DECRYPTION & INTEGRITY CHECK               ")
print("================================================================================")

cipher_dec = AES.new(key, AES.MODE_CBC, iv)
raw_decrypted = cipher_dec.decrypt(tampered)

try:
    tampered_decrypted = unpad(raw_decrypted, 16)
    print("Decrypted payload (padding intact but content damaged).")
except ValueError:
    tampered_decrypted = raw_decrypted
    print("Decrypted payload (padding corrupted, raw decrypted stream retained).")

with open("patient_report_TAMPERED_decrypted.txt", "wb") as f:
    f.write(tampered_decrypted)

# STEP 4 — Compute hash of tampered output
hash_tampered = compute_hash(tampered_decrypted)

# STEP 5 — Compare against original expected hash
print("\n--- Integrity Verification Comparison ---")
print(f"Expected SHA-256 (Original) : {hash_original}")
print(f"Calculated SHA-256 (Tampered): {hash_tampered}")

if hash_original != hash_tampered:
    print("\n🚨 ALERT: Hash mismatch — tampering detected!")
    print("❌ Document integrity check failed! The corrupted file was immediately rejected.")
    print("🔒 Security Takeaway: Due to SHA-256 avalanche properties and collision resistance,")
    print("   modifying even 2 bytes in the ciphertext produces a completely distinct hash digest.")
else:
    print("\nVerification unexpectedly passed.")
