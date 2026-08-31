# ==============================================================================
# Script 1 (Task B1): rsa_keygen.py
# Purpose: Generate 2048-bit RSA Key Pair for Receiver (Public & Private Keys)
# ==============================================================================

from Crypto.PublicKey import RSA
import sys
import os

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("Generating 2048-bit RSA key pair...")

# STEP 1 — Generate RSA key pair
key = RSA.generate(2048)       # 2048-bit key size for robust security

private_key = key.export_key()
public_key  = key.publickey().export_key()

# Save keys to files
with open("receiver_private.pem", "wb") as f:
    f.write(private_key)

with open("receiver_public.pem", "wb") as f:
    f.write(public_key)

print("\n--- Keys Successfully Generated and Saved ---")
print("1. receiver_private.pem -> [SECRET] Kept private by Receiver to DECRYPT session keys.")
print("2. receiver_public.pem  -> [PUBLIC] Freely shared with Sender to ENCRYPT session keys.")
print(f"Key length: {key.size_in_bits()} bits ({len(private_key)} bytes private PEM, {len(public_key)} bytes public PEM)")
