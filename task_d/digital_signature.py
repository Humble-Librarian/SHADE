# ==============================================================================
# Script 1 (Task D1): digital_signature.py
# Purpose: RSA-2048 (PKCS#1 v1.5) Digital Signature Creation, Verification & Tamper Test
# ==============================================================================

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
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

print("================================================================================")
print("                    SENDER SIDE — GENERATE KEYS & SIGN HASH                     ")
print("================================================================================")

# STEP 1 — Generate Sender's own RSA key pair
print("Generating 2048-bit RSA key pair for Sender (Dr. Sender)...")
sender_key = RSA.generate(2048)

sender_private_pem = sender_key.export_key()
sender_public_pem  = sender_key.publickey().export_key()

with open("sender_private.pem", "wb") as f:
    f.write(sender_private_pem)

with open("sender_public.pem", "wb") as f:
    f.write(sender_public_pem)

print("Saved Sender Key Pair:")
print("  - sender_private.pem [SECRET] -> Used by Sender to sign hashes")
print("  - sender_public.pem  [PUBLIC] -> Shared with Receiver to verify signatures")

# STEP 2 — Load document and compute SHA-256 hash object
report_path = find_file("patient_report.txt")
with open(report_path, "rb") as f:
    document_data = f.read()

hash_object = SHA256.new(document_data)
print(f"\nDocument Loaded: {report_path} ({len(document_data)} bytes)")
print(f"SHA-256 Hash Digest: {hash_object.hexdigest()}")

# STEP 3 — Sign the hash using Sender's private key
signer = pkcs1_15.new(sender_key)
signature = signer.sign(hash_object)

with open("document_signature.bin", "wb") as f:
    f.write(signature)

print(f"Generated RSA Digital Signature -> document_signature.bin ({len(signature)} bytes)")
print(f"Signature (hex preview): {signature.hex()[:32]}...")

print("\n================================================================================")
print("                 RECEIVER SIDE — VERIFY DIGITAL SIGNATURE                       ")
print("================================================================================")

# STEP 1 — Load Sender's Public Key
with open("sender_public.pem", "rb") as f:
    sender_public_key = RSA.import_key(f.read())

# STEP 2 — Recompute hash of received document
with open(report_path, "rb") as f:
    received_document = f.read()

received_hash = SHA256.new(received_document)

# STEP 3 — Verify signature
verifier = pkcs1_15.new(sender_public_key)
try:
    verifier.verify(received_hash, signature)
    print("✅ Signature Valid — document is authentic")
    print("🔒 Authenticity & Non-Repudiation Confirmed: Sent by the real Sender and unmodified in transit.")
except (ValueError, TypeError):
    print("❌ Signature Invalid — document forged or tampered!")

print("\n================================================================================")
print("                   TAMPER TEST — VERIFYING TAMPERED DOCUMENT                    ")
print("================================================================================")

# Modify one byte in the document data
tampered_document = bytearray(received_document)
tampered_document[0] ^= 0x01   # Flip a single bit in the first byte
tampered_document = bytes(tampered_document)

tampered_hash = SHA256.new(tampered_document)
print(f"Original Document Hash : {received_hash.hexdigest()}")
print(f"Tampered Document Hash : {tampered_hash.hexdigest()}")

try:
    verifier.verify(tampered_hash, signature)
    print("Verification unexpectedly passed on tampered data.")
except (ValueError, TypeError):
    print("❌ Signature Invalid — tampering detected! Modified document rejected.")
    print("🔒 Proof of Non-Repudiation: The cryptographic signature is strictly tied to the exact hash.")
