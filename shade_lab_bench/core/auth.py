"""Signature, certificate, and Kerberos demonstration primitives."""

import datetime
import json

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import pad, unpad
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def sign_and_verify(document: bytes, private_key: bytes | None = None) -> dict:
    """Sign a SHA-256 digest and verify both original and one-bit-tampered data."""
    sender_key = RSA.import_key(private_key) if private_key else RSA.generate(2048)
    public_key = sender_key.publickey()
    digest = SHA256.new(document)
    signature = pkcs1_15.new(sender_key).sign(digest)
    try:
        pkcs1_15.new(public_key).verify(SHA256.new(document), signature)
        valid = True
    except (ValueError, TypeError):
        valid = False
    tampered = bytearray(document)
    if tampered:
        tampered[0] ^= 0x01
    tampered = bytes(tampered)
    try:
        pkcs1_15.new(public_key).verify(SHA256.new(tampered), signature)
        tamper_detected = False
    except (ValueError, TypeError):
        tamper_detected = True
    return {
        "private_key": sender_key.export_key(), "public_key": public_key.export_key(),
        "signature": signature, "hash": digest.hexdigest(), "valid": valid,
        "tampered_hash": SHA256.new(tampered).hexdigest(), "tamper_detected": tamper_detected,
    }


def generate_x509_certificate(private_key_pem: bytes | None = None, days: int = 365) -> dict:
    """Create and parse the original self-signed SHA-256 X.509 certificate."""
    private_key = (serialization.load_pem_private_key(private_key_pem, password=None)
                   if private_key_pem else rsa.generate_private_key(public_exponent=65537, key_size=2048))
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Gujarat"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SHADE Hospital Network"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Dr. Sender"),
    ])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
            .public_key(private_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now).not_valid_after(now + datetime.timedelta(days=days))
            .sign(private_key, hashes.SHA256()))
    certificate = cert.public_bytes(serialization.Encoding.PEM)
    loaded = x509.load_pem_x509_certificate(certificate)
    valid = loaded.not_valid_before_utc <= now <= loaded.not_valid_after_utc
    return {
        "certificate": certificate, "private_key": private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()),
        "subject": loaded.subject.rfc4514_string(), "issuer": loaded.issuer.rfc4514_string(),
        "serial_number": loaded.serial_number, "valid": valid,
        "public_key_bits": loaded.public_key().key_size,
        "valid_until": loaded.not_valid_after_utc,
    }


def _encrypt_ticket(data: dict, key: bytes) -> bytes:
    iv = get_random_bytes(16)
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(json.dumps(data).encode(), 16))
    return iv + ciphertext


def _decrypt_ticket(blob: bytes, key: bytes) -> dict:
    return json.loads(unpad(AES.new(key, AES.MODE_CBC, blob[:16]).decrypt(blob[16:]), 16).decode())


def simulate_kerberos(client_name: str = "Dr. Sender", service_name: str = "HospitalRecordServer") -> dict:
    """Run the original ticket-granting exchange entirely in memory."""
    tgs_key, service_key = get_random_bytes(16), get_random_bytes(16)
    tgs_session = get_random_bytes(16)
    now = datetime.datetime.now(datetime.timezone.utc)
    tgt = _encrypt_ticket({"client": client_name, "timestamp": now.isoformat(),
                           "session_key": tgs_session.hex(), "expires": (now + datetime.timedelta(hours=8)).isoformat()}, tgs_key)
    recovered_tgt = _decrypt_ticket(tgt, tgs_key)
    service_ticket = _encrypt_ticket({"client": recovered_tgt["client"], "service": service_name,
                                      "session_key": get_random_bytes(16).hex(),
                                      "expires": (now + datetime.timedelta(hours=4)).isoformat()}, service_key)
    recovered_ticket = _decrypt_ticket(service_ticket, service_key)
    return {"tgt": tgt, "service_ticket": service_ticket, "ticket": recovered_ticket,
            "access_granted": recovered_ticket["client"] == client_name and recovered_ticket["service"] == service_name}
