# ==============================================================================
# Script 2 (Task B1): hybrid_encrypt.py
# Purpose: RSA-OAEP + AES-128 CBC Hybrid Envelope Encryption & Decryption
# ==============================================================================

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
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
    raise FileNotFoundError(f"Could not find required file: '{filename}' in current or parent folder.")

print("================================================================================")
print("                        SENDER SIDE — ENCRYPT SESSION KEY                       ")
print("================================================================================")

# STEP 1 — Load Task A artifacts
key_path = find_file("key.bin")
iv_path = find_file("iv.bin")
cipher_path = find_file("patient_report_AES_encrypted.bin")
orig_path = find_file("patient_report.txt")
pubkey_path = find_file("receiver_public.pem")

with open(key_path, "rb") as f:
    aes_key = f.read()

with open(iv_path, "rb") as f:
    iv = f.read()

with open(cipher_path, "rb") as f:
    ciphertext = f.read()

with open(orig_path, "rb") as f:
    original_plaintext = f.read()

print(f"Loaded AES Key ({len(aes_key)} bytes) from: {key_path}")
print(f"Loaded AES IV ({len(iv)} bytes) from: {iv_path}")
print(f"Loaded Encrypted Document ({len(ciphertext)} bytes) from: {cipher_path}")

# STEP 2 — Load Receiver's public key
with open(pubkey_path, "rb") as f:
    pub_key = RSA.import_key(f.read())

print(f"Loaded Receiver's Public RSA Key from: {pubkey_path}")

# STEP 3 — Encrypt the AES key using RSA (PKCS1_OAEP)
cipher_rsa = PKCS1_OAEP.new(pub_key)
encrypted_aes_key = cipher_rsa.encrypt(aes_key)

with open("encrypted_aes_key.bin", "wb") as f:
    f.write(encrypted_aes_key)

print(f"Encrypted AES key using RSA-OAEP -> encrypted_aes_key.bin ({len(encrypted_aes_key)} bytes)")

# STEP 4 — Transmission package summary
print("\n--- Transmission Package for Receiver ---")
print("1. encrypted_aes_key.bin          -> [ENCRYPTED] RSA-encrypted 128-bit AES session key")
print("2. iv.bin                         -> [PUBLIC/PARAM] Initialization vector for AES-CBC")
print("3. patient_report_AES_encrypted.bin -> [ENCRYPTED] Ciphertext payload")

print("\n================================================================================")
print("                       RECEIVER SIDE — DECRYPT & RECOVER                        ")
print("================================================================================")

# STEP 1 — Load Receiver's private key
privkey_path = find_file("receiver_private.pem")
with open(privkey_path, "rb") as f:
    priv_key = RSA.import_key(f.read())

print(f"Loaded Receiver's Private Key from: {privkey_path}")

# STEP 2 — Decrypt the AES key using RSA private key
cipher_rsa_dec = PKCS1_OAEP.new(priv_key)
recovered_aes_key = cipher_rsa_dec.decrypt(encrypted_aes_key)
print(f"Decrypted RSA envelope -> Recovered AES Key ({len(recovered_aes_key)} bytes)")

# STEP 3 — Decrypt the patient document using recovered AES key and IV
cipher_aes_dec = AES.new(recovered_aes_key, AES.MODE_CBC, iv)
recovered_plaintext = unpad(cipher_aes_dec.decrypt(ciphertext), 16)

with open("patient_report_hybrid_decrypted.txt", "wb") as f:
    f.write(recovered_plaintext)

print("Decrypted document saved to: patient_report_hybrid_decrypted.txt")

# STEP 4 — Verification
if recovered_plaintext == original_plaintext:
    print("\n✅ Hybrid decryption successful — recovered file matches original perfectly!")
    print("🔒 Proof of Security: The AES key was transmitted strictly in RSA-OAEP ciphertext form.")
else:
    print("\n❌ Verification Failed: Plaintext mismatch!")
