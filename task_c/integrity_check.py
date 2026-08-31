# ==============================================================================
# Script 1 (Task C): integrity_check.py
# Purpose: SHA-256 Hash Verification for Document Integrity Before & After Transit
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

def compute_hash(filepath_or_bytes):
    if isinstance(filepath_or_bytes, bytes):
        data = filepath_or_bytes
    else:
        with open(filepath_or_bytes, "rb") as f:
            data = f.read()
    h = SHA256.new(data)
    return h.hexdigest()

print("================================================================================")
print("                    SENDER SIDE — COMPUTE ORIGINAL HASH                         ")
print("================================================================================")

orig_report_path = find_file("patient_report.txt")
hash_original = compute_hash(orig_report_path)

# Save original hash to original_hash.txt
with open("original_hash.txt", "w", encoding="utf-8") as f:
    f.write(hash_original)

print(f"Original Document : {orig_report_path}")
print(f"SHA-256 (original): {hash_original}")
print("Saved hash digest -> original_hash.txt")

print("\n--- Transmission Package Transmitted to Receiver ---")
print("1. patient_report_AES_encrypted.bin  (Encrypted document payload)")
print("2. encrypted_aes_key.bin             (RSA-encrypted session key)")
print("3. iv.bin                            (AES Initialization Vector)")
print("4. original_hash.txt                 (Cryptographic SHA-256 checksum)")

print("\n================================================================================")
print("                   RECEIVER SIDE — DECRYPT & VERIFY INTEGRITY                   ")
print("================================================================================")

# Receiver receives ciphertext, key, iv
key_path = find_file("key.bin")
iv_path = find_file("iv.bin")
cipher_path = find_file("patient_report_AES_encrypted.bin")

with open(key_path, "rb") as f:
    key = f.read()

with open(iv_path, "rb") as f:
    iv = f.read()

with open(cipher_path, "rb") as f:
    ciphertext = f.read()

# Decrypt document
cipher_dec = AES.new(key, AES.MODE_CBC, iv)
decrypted_bytes = unpad(cipher_dec.decrypt(ciphertext), 16)

with open("patient_report_integrity_decrypted.txt", "wb") as f:
    f.write(decrypted_bytes)

# Compute hash of received/decrypted document
hash_received = compute_hash("patient_report_integrity_decrypted.txt")
print(f"SHA-256 (received): {hash_received}")

# Compare hashes
print("\n--- Integrity Verification Result ---")
if hash_original == hash_received:
    print("✅ Integrity Verified — hashes match perfectly!")
    print("🔒 Proof: The document was NOT tampered with or corrupted during transmission.")
else:
    print("❌ Integrity Check FAILED — file tampered!")
