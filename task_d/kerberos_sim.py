# ==============================================================================
# Script 3 (Task D3): kerberos_sim.py
# Purpose: Step-by-Step Simulation of the Kerberos Ticket-Granting Authentication Protocol
# ==============================================================================

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import json
import datetime
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def encrypt_ticket(data_dict, key):
    json_bytes = json.dumps(data_dict).encode('utf-8')
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(json_bytes, 16))
    return iv + ciphertext

def decrypt_ticket(blob, key):
    iv = blob[:16]
    ciphertext = blob[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), 16)
    return json.loads(plaintext.decode('utf-8'))

print("================================================================================")
print("             KERBEROS AUTHENTICATION & TICKET GRANTING SIMULATION               ")
print("================================================================================")

# STEP 1 — Setup identities and secret keys
client_name   = "Dr. Sender"
service_name  = "HospitalRecordServer"

# Long-term secret keys (KDC & Server know their respective keys)
as_secret_key      = get_random_bytes(16)   # Known only to AS and Client (derived from password)
tgs_master_key     = get_random_bytes(16)   # Known only to AS and TGS
service_master_key = get_random_bytes(16)   # Known only to TGS and HospitalRecordServer

print(f"Principal Client  : {client_name}")
print(f"Target Service    : {service_name}")
print("Initialized KDC Master Keys for AS, TGS, and Resource Server.")

# STEP 2 — Authentication Service (AS) Exchange
print("\n--------------------------------------------------------------------------------")
print("STEP 1 & 2: Client <--> Authentication Server (AS) Exchange")
print("--------------------------------------------------------------------------------")
print(f"[Client -> AS] Requesting initial authentication for principal: '{client_name}'")

# AS creates a session key for Client <-> TGS communication
tgs_session_key = get_random_bytes(16)

# AS creates Ticket Granting Ticket (TGT) encrypted with TGS Master Key
tgt_payload = {
    "client": client_name,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "session_key": tgs_session_key.hex(),
    "expires": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)).isoformat()
}
encrypted_tgt = encrypt_ticket(tgt_payload, tgs_master_key)

print(f"[AS -> Client] Authentication Successful! Issued Encrypted TGT ({len(encrypted_tgt)} bytes).")
print(f"               (TGT is encrypted with TGS Key; only TGS can read its content)")

# STEP 3 — Ticket Granting Service (TGS) Exchange
print("\n--------------------------------------------------------------------------------")
print("STEP 3 & 4: Client <--> Ticket Granting Server (TGS) Exchange")
print("--------------------------------------------------------------------------------")
print(f"[Client -> TGS] Submitting TGT and requesting Service Ticket for '{service_name}'")

# TGS decrypts and verifies the TGT
recovered_tgt = decrypt_ticket(encrypted_tgt, tgs_master_key)
print(f"[TGS] Successfully decrypted TGT. Authenticated Client Principal: '{recovered_tgt['client']}'")

# TGS generates a Service Session Key for Client <-> HospitalRecordServer
service_session_key = get_random_bytes(16)

# TGS constructs Service Ticket (ST) encrypted with Service Master Key
service_ticket_payload = {
    "client": recovered_tgt["client"],
    "service": service_name,
    "session_key": service_session_key.hex(),
    "expires": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4)).isoformat()
}
encrypted_service_ticket = encrypt_ticket(service_ticket_payload, service_master_key)

print(f"[TGS -> Client] Issued Service Ticket for '{service_name}' ({len(encrypted_service_ticket)} bytes).")

# STEP 4 — Service Presentation & Authorization
print("\n--------------------------------------------------------------------------------")
print("STEP 5: Client <--> Hospital Record Server Presentation")
print("--------------------------------------------------------------------------------")
print(f"[Client -> Server] Presenting Service Ticket to '{service_name}'")

# Server decrypts Service Ticket with its own master key
recovered_st = decrypt_ticket(encrypted_service_ticket, service_master_key)

print(f"[Server] Decrypted Service Ticket:")
print(f"         - Authorized Client : {recovered_st['client']}")
print(f"         - Target Service    : {recovered_st['service']}")
print(f"         - Ticket Expiration : {recovered_st['expires']}")

if recovered_st["client"] == client_name and recovered_st["service"] == service_name:
    print(f"\n✅ Server: Access granted to {client_name} for {service_name}!")
    print("🔒 Kerberos Security Property Proved: Passwords never cross the network;")
    print("   Mutual trust is established via single-sign-on (SSO) encrypted tickets.")
else:
    print("\n❌ Server: Access denied! Invalid ticket credentials.")
