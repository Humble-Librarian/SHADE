# ==============================================================================
# Script 2 (Task D2): x509_cert_sim.py
# Purpose: Generate and Validate a Self-Signed X.509 Digital Certificate
# ==============================================================================

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
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
    raise FileNotFoundError(f"Could not find required file: '{filename}'")

print("================================================================================")
print("                   X.509 DIGITAL CERTIFICATE GENERATION (PKI)                   ")
print("================================================================================")

# STEP 1 — Load Sender's private key (or generate if needed)
if os.path.exists("sender_private.pem"):
    with open("sender_private.pem", "rb") as f:
        sender_private_key = serialization.load_pem_private_key(f.read(), password=None)
    print("Loaded Sender's Private Key from: sender_private.pem")
else:
    print("sender_private.pem not found. Generating a new 2048-bit RSA key for Sender...")
    sender_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

sender_public_key = sender_private_key.public_key()

# STEP 2 — Define X.509 Subject & Issuer identity fields
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Gujarat"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SHADE Hospital Network"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Dr. Sender"),
])

# STEP 3 — Build and self-sign the X.509 certificate
now = datetime.datetime.now(datetime.timezone.utc)
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)                      # Self-signed: Issuer == Subject
    .public_key(sender_public_key)
    .serial_number(x509.random_serial_number())
    .not_valid_before(now)
    .not_valid_after(now + datetime.timedelta(days=365))
    .sign(sender_private_key, hashes.SHA256())
)

cert_pem = cert.public_bytes(serialization.Encoding.PEM)

with open("sender_certificate.pem", "wb") as f:
    f.write(cert_pem)

print("Generated X.509 Certificate -> sender_certificate.pem")
print("🔒 Concept: Certificate binds Doctor's Identity to their Public Key via Digital Signature.")

print("\n================================================================================")
print("             RECEIVER SIDE — CERTIFICATE PARSING & VERIFICATION                 ")
print("================================================================================")

# STEP 4 — Receiver parses and validates certificate fields
with open("sender_certificate.pem", "rb") as f:
    loaded_cert = x509.load_pem_x509_certificate(f.read())

print(f"Subject Identity : {loaded_cert.subject.rfc4514_string()}")
print(f"Issuer (CA)      : {loaded_cert.issuer.rfc4514_string()}")
print(f"Serial Number    : {hex(loaded_cert.serial_number)}")
print(f"Valid From       : {loaded_cert.not_valid_before_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Valid Until      : {loaded_cert.not_valid_after_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Signature Algo   : {loaded_cert.signature_hash_algorithm.name.upper()}")
print(f"Public Key Size  : {loaded_cert.public_key().key_size} bits")

# Verify dates
is_valid_now = loaded_cert.not_valid_before_utc <= now <= loaded_cert.not_valid_after_utc
if is_valid_now:
    print("\n✅ Certificate structure verified and currently within valid date range")
    print("🔒 PKI Assurance: In production, the CA signature guarantees that the public key has not been spoofed.")
else:
    print("\n❌ Certificate validation failed: Expired or not yet valid.")
