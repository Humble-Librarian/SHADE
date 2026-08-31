# ==============================================================================
# Script 4 (Task B3): mitm_attack.py
# Purpose: Simulate Active Man-in-the-Middle (MITM) Interception on Unauthenticated DH
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
print("             MAN-IN-THE-MIDDLE (MITM) ATTACK SIMULATION ON DH                   ")
print("================================================================================")

# STEP 1 — Generate shared DH parameters for all 3 entities
print("Generating Diffie-Hellman parameters (p, g)...")
parameters = dh.generate_parameters(generator=2, key_size=512)

# Sender generates key pair
sender_private = parameters.generate_private_key()
sender_public  = sender_private.public_key()

# Receiver generates key pair
receiver_private = parameters.generate_private_key()
receiver_public  = receiver_private.public_key()

# Mallory (Attacker) generates her own key pair
mallory_private = parameters.generate_private_key()
mallory_public  = mallory_private.public_key()

print("[+] Keys generated for: Sender, Receiver, and Attacker (Mallory)")

# STEP 2 — Simulate Public Key Interception
print("\n--- Network Interception Simulation ---")
print("[1] Sender attempts to send Public Key (A) to Receiver.")
print("    --> ⚠️ Mallory INTERCEPTS 'A' and substitutes with Mallory's Public Key (M).")
print("[2] Receiver attempts to send Public Key (B) to Sender.")
print("    --> ⚠️ Mallory INTERCEPTS 'B' and substitutes with Mallory's Public Key (M).")

# Mallory computes TWO independent shared secrets
mallory_with_sender   = mallory_private.exchange(sender_public)
mallory_with_receiver = mallory_private.exchange(receiver_public)

# Sender and Receiver compute shared secrets using Mallory's public key (thinking it belongs to each other)
sender_shared   = sender_private.exchange(mallory_public)
receiver_shared = receiver_private.exchange(mallory_public)

# STEP 3 — Print Evidence & Key Matching
print("\n--- Shared Secret Analysis ---")
print(f"Sender believes secret is with Receiver : {sender_shared.hex()[:32]}...")
print(f"Mallory's computed secret with Sender   : {mallory_with_sender.hex()[:32]}...")
print(f"Receiver believes secret is with Sender : {receiver_shared.hex()[:32]}...")
print(f"Mallory's computed secret with Receiver : {mallory_with_receiver.hex()[:32]}...")

print("\n--- Attack Verification ---")
if sender_shared == mallory_with_sender and receiver_shared == mallory_with_receiver:
    print("❌ MITM Attack Succeeded!")
    print("   - Sender & Receiver do NOT share a common secret.")
    print(f"   - (Sender != Receiver Secret): {sender_shared != receiver_shared}")
    print("   - Mallory can transparently decrypt, inspect/modify, and re-encrypt all traffic in transit.")
else:
    print("Attack simulation anomaly.")

# STEP 4 — Cryptographic Prevention & Countermeasures
print("\n================================================================================")
print("                           PREVENTION & COUNTERMEASURES                         ")
print("================================================================================")
print("⚠️ Root Cause: Diffie-Hellman provides key secrecy but NO authentication.")
print("🛡️ Mitigation Strategies:")
print("   1. Authenticated DH (Station-to-Station protocol) using Digital Signatures.")
print("   2. Public Key Infrastructure (PKI): Exchange public keys signed by a trusted Certificate Authority (CA).")
print("   3. Transport Layer Security (TLS / HTTPS): Server presents an X.509 certificate to authenticate before ECDHE exchange.")
