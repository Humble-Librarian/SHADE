# ==============================================================================
# Script 3 (Task B2): diffie_hellman.py
# Purpose: Diffie-Hellman Key Exchange (Mutual Shared Secret Derivation)
# ==============================================================================

from cryptography.hazmat.primitives.asymmetric import dh
import sys
import warnings

# Suppress cryptography FFDH educational warning
warnings.filterwarnings("ignore")

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("================================================================================")
print("                     DIFFIE-HELLMAN KEY EXCHANGE SIMULATION                     ")
print("================================================================================")

# STEP 1 — Generate shared DH parameters (p and g)
print("Generating Diffie-Hellman parameters (p, g)...")
parameters = dh.generate_parameters(generator=2, key_size=512)
param_numbers = parameters.parameter_numbers()
print(f"Generator (g): {param_numbers.g}")
print(f"Modulus (p, prime): {hex(param_numbers.p)[:32]}... ({param_numbers.p.bit_length()} bits)")

# STEP 2 — Sender generates private + public key
sender_private = parameters.generate_private_key()
sender_public  = sender_private.public_key()
print("\n[Sender] Generated private key (a) and computed public value A = g^a mod p")

# STEP 3 — Receiver generates private + public key
receiver_private = parameters.generate_private_key()
receiver_public  = receiver_private.public_key()
print("[Receiver] Generated private key (b) and computed public value B = g^b mod p")

# STEP 4 — Exchange public keys and compute shared secret
# Sender computes: shared = B^a mod p
# Receiver computes: shared = A^b mod p
sender_shared   = sender_private.exchange(receiver_public)
receiver_shared = receiver_private.exchange(sender_public)

print("\n--- Key Exchange Verification ---")
print(f"Sender computed shared secret   : {sender_shared.hex()}")
print(f"Receiver computed shared secret : {receiver_shared.hex()}")

# STEP 5 — Verify both are equal
if sender_shared == receiver_shared:
    print("\n✅ DH Key Exchange Successful — shared secret matches exactly!")
    print(f"Derived Shared Secret (32-byte hex preview): {sender_shared.hex()[:32]}...")
    print(f"Total Shared Secret Length: {len(sender_shared)} bytes")
    print("🔒 Concept Proved: Both parties independently derived identical keying material without transmitting the secret.")
else:
    print("\n❌ Error: Shared secret mismatch!")
