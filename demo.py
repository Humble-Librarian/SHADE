"""
================================================================================
  SHADE — Secure Hospital And Document Exchange
  Full End-to-End Cryptographic Pipeline Demo
================================================================================
  Run: python demo.py
  Requires: pip install pycryptodome cryptography Pillow
================================================================================
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import os, time, json, datetime, sys, warnings

# Suppress cryptography educational deprecation warning for FFDH demo
warnings.filterwarnings("ignore")

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# PyCryptodome
from Crypto.Cipher    import AES, DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher    import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash      import SHA256
from Crypto.Util.Padding import pad, unpad
from Crypto.Random    import get_random_bytes

# cryptography (for DH and X.509)
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives            import hashes, serialization
from cryptography                              import x509
from cryptography.x509.oid                    import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa

# Pillow (for ECB vs CBC image)
from PIL import Image, ImageDraw

# ── Helpers ───────────────────────────────────────────────────────────────────
RESULTS = {}

def banner(text):
    print("\n" + "=" * 72)
    print(f"  {text}")
    print("=" * 72)

def phase(n, title):
    print(f"\n{'─' * 72}")
    print(f"  PHASE {n} — {title}")
    print(f"{'─' * 72}")

def ok(label, detail=""):
    RESULTS[label] = True
    suffix = f"  {detail}" if detail else ""
    print(f"  [✅] {label}{suffix}")

def fail(label, detail=""):
    RESULTS[label] = False
    suffix = f"  {detail}" if detail else ""
    print(f"  [❌] {label}{suffix}")

def info(msg):
    print(f"  [·] {msg}")

def warn(msg):
    print(f"  [!] {msg}")

def sha256_file(path):
    with open(path, "rb") as f:
        return SHA256.new(f.read()).hexdigest()

def sha256_bytes(data):
    return SHA256.new(data).hexdigest()

# ── Phase 0 — Setup ───────────────────────────────────────────────────────────
def phase_0_setup():
    phase(0, "SETUP")

    if not os.path.exists("patient_report.txt"):
        fail("patient_report.txt", "FILE NOT FOUND — place it next to demo.py")
        raise SystemExit(1)

    with open("patient_report.txt", "rb") as f:
        data = f.read()
    info(f"Loaded patient_report.txt ({len(data)} bytes)")

    # clean up any leftover files from previous runs
    stale = [
        "key.bin", "iv.bin",
        "patient_report_AES_encrypted.bin", "patient_report_AES_decrypted.txt",
        "patient_report_3DES_encrypted.bin", "patient_report_3DES_decrypted.txt",
        "patient_report_TAMPERED.bin",
        "sample.bmp", "ecb_output.bmp", "cbc_output.bmp",
        "encrypted_aes_key.bin",
        "receiver_private.pem", "receiver_public.pem",
        "sender_private.pem",   "sender_public.pem",
        "document_signature.bin", "sender_certificate.pem",
        "original_hash.txt",
    ]
    cleaned = sum(1 for f in stale if os.path.exists(f) and not os.remove(f))
    info(f"Cleaned {cleaned} stale file(s) from previous run")
    ok("Setup", "workspace ready")

# ── Phase 1 — Task A ──────────────────────────────────────────────────────────
def phase_1_task_a():
    phase(1, "SYMMETRIC ENCRYPTION LAYER  (Task A)")

    with open("patient_report.txt", "rb") as f:
        plaintext = f.read()

    # ── AES-128 CBC ──────────────────────────────────────────────────────────
    info("Generating AES-128 key (16B) and IV (16B)...")
    aes_key = get_random_bytes(16)
    aes_iv  = get_random_bytes(16)
    with open("key.bin", "wb") as f: f.write(aes_key)
    with open("iv.bin",  "wb") as f: f.write(aes_iv)

    info("Encrypting with AES-128 CBC...")
    cipher    = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16))
    with open("patient_report_AES_encrypted.bin", "wb") as f:
        f.write(ciphertext)

    info("Decrypting to verify...")
    cipher_d  = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    decrypted = unpad(cipher_d.decrypt(ciphertext), 16)
    with open("patient_report_AES_decrypted.txt", "wb") as f:
        f.write(decrypted)

    if decrypted == plaintext:
        ok("AES-128 CBC Encryption", f"{len(plaintext)}B → {len(ciphertext)}B cipher → recovered")
    else:
        fail("AES-128 CBC Encryption", "decryption mismatch")

    # ── 3-DES CBC ────────────────────────────────────────────────────────────
    info("Encrypting with 3-DES CBC...")
    des_key = get_random_bytes(24)
    des_iv  = get_random_bytes(8)
    cipher3  = DES3.new(des_key, DES3.MODE_CBC, des_iv)
    ct3      = cipher3.encrypt(pad(plaintext, 8))
    with open("patient_report_3DES_encrypted.bin", "wb") as f:
        f.write(ct3)

    cipher3d  = DES3.new(des_key, DES3.MODE_CBC, des_iv)
    dec3      = unpad(cipher3d.decrypt(ct3), 8)
    with open("patient_report_3DES_decrypted.txt", "wb") as f:
        f.write(dec3)

    if dec3 == plaintext:
        ok("3-DES CBC Encryption", f"{len(plaintext)}B → {len(ct3)}B cipher → recovered")
    else:
        fail("3-DES CBC Encryption", "decryption mismatch")

    # ── Timing comparison ────────────────────────────────────────────────────
    info("Timing benchmark — AES vs 3-DES (3 file sizes)...")
    sizes = {"1 KB": 1_024, "100 KB": 102_400, "1 MB": 1_048_576}
    print()
    print(f"  {'File Size':<10} {'AES-128 (ms)':<16} {'3-DES (ms)':<16} {'Speedup'}")
    print(f"  {'─'*10} {'─'*15} {'─'*15} {'─'*10}")
    for label, sz in sizes.items():
        sample = os.urandom(sz)
        t0 = time.perf_counter()
        AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(sample, 16))
        aes_t = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        DES3.new(des_key, DES3.MODE_CBC, des_iv).encrypt(pad(sample, 8))
        des_t = (time.perf_counter() - t0) * 1000

        print(f"  {label:<10} {aes_t:<16.4f} {des_t:<16.4f} ~{des_t/aes_t:.1f}x faster (AES)")
    print()

    # ── Avalanche Effect ─────────────────────────────────────────────────────
    info("Avalanche Effect — 1-bit flip, same key & IV...")
    modified = bytearray(plaintext)
    modified[0] ^= 0x01
    modified = bytes(modified)

    ct_orig = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(plaintext, 16))
    ct_mod  = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(modified,  16))

    length     = min(len(ct_orig), len(ct_mod))
    diff_bits  = sum(bin(ct_orig[i] ^ ct_mod[i]).count('1') for i in range(length))
    total_bits = length * 8
    pct        = diff_bits / total_bits * 100

    if 45 <= pct <= 55:
        ok("Avalanche Effect", f"{diff_bits}/{total_bits} bits changed → {pct:.2f}% (ideal 45–55%)")
    else:
        fail("Avalanche Effect", f"{pct:.2f}% — outside ideal range")

    # ── ECB vs CBC Image ─────────────────────────────────────────────────────
    info("Generating ECB vs CBC image comparison...")
    img = Image.new("RGB", (256, 256), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 215, 215], fill="blue")
    draw.rectangle([80, 80, 175, 175], fill="white")
    draw.rectangle([100, 100, 155, 155], fill="blue")
    img.save("sample.bmp")

    with open("sample.bmp", "rb") as f:
        header     = f.read(54)
        pixel_data = f.read()

    img_key = get_random_bytes(16)
    img_iv  = get_random_bytes(16)

    padded  = pad(pixel_data, 16)

    ecb_enc = AES.new(img_key, AES.MODE_ECB).encrypt(padded)[:len(pixel_data)]
    with open("ecb_output.bmp", "wb") as f: f.write(header + ecb_enc)

    cbc_enc = AES.new(img_key, AES.MODE_CBC, img_iv).encrypt(padded)[:len(pixel_data)]
    with open("cbc_output.bmp", "wb") as f: f.write(header + cbc_enc)

    ok("ECB vs CBC Image", "sample.bmp | ecb_output.bmp | cbc_output.bmp saved")

# ── Phase 2 — Task B ──────────────────────────────────────────────────────────
def phase_2_task_b():
    phase(2, "ASYMMETRIC ENCRYPTION & KEY EXCHANGE  (Task B)")

    with open("patient_report.txt", "rb") as f: plaintext = f.read()
    with open("key.bin",  "rb") as f: aes_key = f.read()
    with open("iv.bin",   "rb") as f: aes_iv  = f.read()
    with open("patient_report_AES_encrypted.bin", "rb") as f: ciphertext = f.read()

    # ── RSA-2048 Key Generation ───────────────────────────────────────────────
    info("Generating RSA-2048 key pair for Receiver...")
    rsa_key  = RSA.generate(2048)
    priv_pem = rsa_key.export_key()
    pub_pem  = rsa_key.publickey().export_key()
    with open("receiver_private.pem", "wb") as f: f.write(priv_pem)
    with open("receiver_public.pem",  "wb") as f: f.write(pub_pem)
    ok("RSA-2048 Key Generation",
       f"private ({len(priv_pem)}B) + public ({len(pub_pem)}B)")

    # ── Hybrid Envelope Encryption ────────────────────────────────────────────
    info("Hybrid Envelope — Sender encrypts AES key with RSA-OAEP...")
    pub_key     = RSA.import_key(pub_pem)
    cipher_rsa  = PKCS1_OAEP.new(pub_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)
    with open("encrypted_aes_key.bin", "wb") as f: f.write(enc_aes_key)
    info(f"encrypted_aes_key.bin ({len(enc_aes_key)}B) — AES key wrapped in RSA ciphertext")

    info("Receiver decrypts envelope and recovers document...")
    priv_key       = RSA.import_key(priv_pem)
    cipher_rsa_d   = PKCS1_OAEP.new(priv_key)
    recovered_key  = cipher_rsa_d.decrypt(enc_aes_key)
    cipher_d       = AES.new(recovered_key, AES.MODE_CBC, aes_iv)
    recovered_doc  = unpad(cipher_d.decrypt(ciphertext), 16)
    with open("patient_report_hybrid_decrypted.txt", "wb") as f:
        f.write(recovered_doc)

    if recovered_doc == plaintext:
        ok("Hybrid Envelope Encryption", "AES key wrapped → unwrapped → document recovered")
    else:
        fail("Hybrid Envelope Encryption", "document mismatch after hybrid decrypt")

    # ── Diffie-Hellman Key Exchange ───────────────────────────────────────────
    info("Generating Diffie-Hellman parameters (512-bit, g=2)...")
    params      = dh.generate_parameters(generator=2, key_size=512)
    sender_priv = params.generate_private_key()
    recv_priv   = params.generate_private_key()
    sender_pub  = sender_priv.public_key()
    recv_pub    = recv_priv.public_key()

    sender_shared   = sender_priv.exchange(recv_pub)
    receiver_shared = recv_priv.exchange(sender_pub)

    if sender_shared == receiver_shared:
        ok("Diffie-Hellman Key Exchange",
           f"shared secret: {sender_shared.hex()[:16]}... (both match)")
    else:
        fail("Diffie-Hellman Key Exchange", "shared secrets do not match")

    # ── MITM Attack Simulation ────────────────────────────────────────────────
    info("MITM Attack — Mallory intercepts unauthenticated DH exchange...")
    mallory_priv = params.generate_private_key()
    mallory_pub  = mallory_priv.public_key()

    warn("Mallory intercepts Sender's public key (A) → substitutes her own")
    warn("Mallory intercepts Receiver's public key (B) → substitutes her own")

    sender_thinks   = sender_priv.exchange(mallory_pub)
    receiver_thinks = recv_priv.exchange(mallory_pub)
    mallory_s       = mallory_priv.exchange(sender_pub)
    mallory_r       = mallory_priv.exchange(recv_pub)

    print(f"\n  Sender  believes secret: {sender_thinks.hex()[:24]}...")
    print(f"  Mallory↔Sender  secret : {mallory_s.hex()[:24]}...")
    print(f"  Receiver believes secret:{receiver_thinks.hex()[:24]}...")
    print(f"  Mallory↔Receiver secret: {mallory_r.hex()[:24]}...")

    if sender_thinks == mallory_s and receiver_thinks == mallory_r:
        ok("MITM Simulation",
           "Sender & Receiver hold different secrets — Mallory in the middle")
        warn("Prevention: Authenticated DH (X.509 certs / TLS / PKI)")
    else:
        fail("MITM Simulation", "unexpected result")

# ── Phase 3 — Task C ──────────────────────────────────────────────────────────
def phase_3_task_c():
    phase(3, "INTEGRITY LAYER  (Task C)")

    # ── SHA-256 Integrity Check ───────────────────────────────────────────────
    info("Computing SHA-256 of original patient_report.txt...")
    original_hash = sha256_file("patient_report.txt")
    with open("original_hash.txt", "w") as f: f.write(original_hash)
    print(f"\n  Original SHA-256 : {original_hash}\n")

    info("Receiver decrypts and verifies hash...")
    with open("patient_report.txt", "rb") as f: plaintext = f.read()
    with open("key.bin",  "rb") as f: aes_key = f.read()
    with open("iv.bin",   "rb") as f: aes_iv  = f.read()
    with open("patient_report_AES_encrypted.bin", "rb") as f: ct = f.read()

    decrypted     = unpad(AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(ct), 16)
    received_hash = sha256_bytes(decrypted)

    if original_hash == received_hash:
        ok("SHA-256 Integrity Check", "hashes match — document untampered")
    else:
        fail("SHA-256 Integrity Check", "hash mismatch")

    # ── Tamper Detection ──────────────────────────────────────────────────────
    info("Simulating in-transit ciphertext tampering (byte 10 and byte 50)...")
    tampered = bytearray(ct)
    tampered[10] ^= 0xFF
    tampered[50] ^= 0xAA
    tampered = bytes(tampered)
    with open("patient_report_TAMPERED.bin", "wb") as f: f.write(tampered)

    try:
        dec_tampered  = unpad(AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(tampered), 16)
        tampered_hash = sha256_bytes(dec_tampered)
    except Exception:
        tampered_hash = "PADDING_ERROR_" + get_random_bytes(8).hex()

    print(f"\n  Expected (original) : {original_hash}")
    print(f"  Calculated (tampered): {tampered_hash}")

    if original_hash != tampered_hash:
        ok("Tamper Detection", "hash mismatch alert triggered — corrupted file rejected")
    else:
        fail("Tamper Detection", "tampered hash unexpectedly matched — check logic")

# ── Phase 4 — Task D ──────────────────────────────────────────────────────────
def phase_4_task_d():
    phase(4, "AUTHENTICATION LAYER  (Task D)")

    with open("patient_report.txt", "rb") as f: plaintext = f.read()

    # ── RSA Digital Signature ─────────────────────────────────────────────────
    info("Generating RSA-2048 key pair for Sender (Dr. Kavya Sharma)...")
    sender_key     = RSA.generate(2048)
    sender_priv_pem = sender_key.export_key()
    sender_pub_pem  = sender_key.publickey().export_key()
    with open("sender_private.pem", "wb") as f: f.write(sender_priv_pem)
    with open("sender_public.pem",  "wb") as f: f.write(sender_pub_pem)

    info("Signing SHA-256 hash of patient_report.txt with Sender's private key...")
    h         = SHA256.new(plaintext)
    signer    = pkcs1_15.new(sender_key)
    signature = signer.sign(h)
    with open("document_signature.bin", "wb") as f: f.write(signature)
    print(f"\n  SHA-256 hash  : {h.hexdigest()}")
    print(f"  Signature (hex): {signature.hex()[:32]}...\n")

    info("Receiver verifies signature using Sender's public key...")
    pub_key  = RSA.import_key(sender_pub_pem)
    verifier = pkcs1_15.new(pub_key)
    try:
        verifier.verify(SHA256.new(plaintext), signature)
        ok("Digital Signature", "valid — document authentic, sender confirmed")
    except (ValueError, TypeError):
        fail("Digital Signature", "signature verification failed")

    info("Tamper test — modifying one byte of document...")
    tampered_doc = bytearray(plaintext)
    tampered_doc[0] ^= 0x01
    try:
        verifier.verify(SHA256.new(bytes(tampered_doc)), signature)
        fail("Signature Tamper Test", "tampered document incorrectly accepted")
    except (ValueError, TypeError):
        ok("Signature Tamper Test", "tampered document correctly rejected")

    # ── X.509 Self-Signed Certificate ─────────────────────────────────────────
    info("Generating X.509 self-signed certificate for Sender...")
    cert_key = crypto_rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME,             "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,   "Gujarat"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME,        "SHADE Hospital Network"),
        x509.NameAttribute(NameOID.COMMON_NAME,              "Dr. Sender"),
    ])
    now  = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(cert_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .sign(cert_key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    with open("sender_certificate.pem", "wb") as f: f.write(cert_pem)

    info("Parsing and validating certificate fields...")
    loaded = x509.load_pem_x509_certificate(cert_pem)
    print(f"\n  Subject    : {loaded.subject.rfc4514_string()}")
    print(f"  Issuer     : {loaded.issuer.rfc4514_string()}")
    print(f"  Valid From : {loaded.not_valid_before_utc.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Valid Until: {loaded.not_valid_after_utc.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Key Size   : {loaded.public_key().key_size} bits")
    print(f"  Sig Algo   : SHA256withRSA\n")

    if loaded.not_valid_before_utc <= now <= loaded.not_valid_after_utc:
        ok("X.509 Certificate", "self-signed, parsed, within validity period")
    else:
        fail("X.509 Certificate", "date validation failed")

    # ── Kerberos Simulation ───────────────────────────────────────────────────
    info("Kerberos ticket-granting simulation (5-step exchange)...")

    client_name  = "Dr. Sender"
    service_name = "HospitalRecordServer"

    as_key  = get_random_bytes(16)   # Authentication Server master key
    tgs_key = get_random_bytes(16)   # Ticket Granting Server key
    svc_key = get_random_bytes(16)   # Service (resource server) key

    def aes_encrypt_data(key, data_dict):
        raw   = json.dumps(data_dict).encode()
        iv    = get_random_bytes(16)
        ct    = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(raw, 16))
        return iv + ct

    def aes_decrypt_data(key, blob):
        iv, ct = blob[:16], blob[16:]
        raw    = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
        return json.loads(raw.decode())

    expiry = (datetime.datetime.now(datetime.timezone.utc)
              + datetime.timedelta(hours=8)).isoformat()

    # Step 1 & 2 — Client ↔ AS
    print(f"\n  [1] {client_name} → AS : requesting authentication")
    tgt_payload = {"client": client_name, "session_key": tgs_key.hex(), "expires": expiry}
    tgt_blob    = aes_encrypt_data(as_key, tgt_payload)
    print(f"  [2] AS → {client_name} : TGT issued ({len(tgt_blob)}B, encrypted with AS key)")

    # Step 3 & 4 — Client ↔ TGS
    print(f"  [3] {client_name} → TGS : submitting TGT, requesting ticket for '{service_name}'")
    tgt_decrypted = aes_decrypt_data(as_key, tgt_blob)
    assert tgt_decrypted["client"] == client_name
    st_payload  = {"client": client_name, "service": service_name,
                   "session_key": svc_key.hex(), "expires": expiry}
    st_blob     = aes_encrypt_data(tgs_key, st_payload)
    print(f"  [4] TGS → {client_name} : Service Ticket issued ({len(st_blob)}B) for '{service_name}'")

    # Step 5 — Client → Service
    print(f"  [5] {client_name} → {service_name} : presenting Service Ticket")
    st_decrypted = aes_decrypt_data(tgs_key, st_blob)
    assert st_decrypted["service"] == service_name
    print(f"      Authorized client : {st_decrypted['client']}")
    print(f"      Target service    : {st_decrypted['service']}")
    print(f"      Ticket expires    : {st_decrypted['expires']}\n")

    ok("Kerberos Authentication", f"TGT({len(tgt_blob)}B) → ST({len(st_blob)}B) → access granted")

# ── Phase 5 — Summary ─────────────────────────────────────────────────────────
def phase_5_summary():
    banner("SHADE PIPELINE — FINAL VERIFICATION SUMMARY")

    checks = [
        "AES-128 CBC Encryption",
        "3-DES CBC Encryption",
        "Avalanche Effect",
        "ECB vs CBC Image",
        "RSA-2048 Key Generation",
        "Hybrid Envelope Encryption",
        "Diffie-Hellman Key Exchange",
        "MITM Simulation",
        "SHA-256 Integrity Check",
        "Tamper Detection",
        "Digital Signature",
        "Signature Tamper Test",
        "X.509 Certificate",
        "Kerberos Authentication",
    ]

    passed = sum(1 for c in checks if RESULTS.get(c))
    total  = len(checks)

    print()
    print(f"  {'Check':<35} {'Status'}")
    print(f"  {'─'*35} {'─'*10}")
    for c in checks:
        status = "✅  PASS" if RESULTS.get(c) else "❌  FAIL"
        print(f"  {c:<35} {status}")
    print(f"  {'─'*35} {'─'*10}")
    print(f"  {'TOTAL':<35} {passed}/{total} passed")
    print()

    if passed == total:
        print("  🔒 All checks passed. SHADE pipeline complete.\n")
    else:
        print(f"  ⚠️  {total - passed} check(s) failed. Review output above.\n")

    # Generated files
    files = [
        "key.bin", "iv.bin",
        "patient_report_AES_encrypted.bin", "patient_report_AES_decrypted.txt",
        "patient_report_3DES_encrypted.bin", "patient_report_3DES_decrypted.txt",
        "patient_report_TAMPERED.bin",
        "sample.bmp", "ecb_output.bmp", "cbc_output.bmp",
        "encrypted_aes_key.bin", "patient_report_hybrid_decrypted.txt",
        "receiver_private.pem", "receiver_public.pem",
        "original_hash.txt",
        "sender_private.pem", "sender_public.pem",
        "document_signature.bin", "sender_certificate.pem",
    ]
    print("  Generated files:")
    for fp in files:
        size = os.path.getsize(fp) if os.path.exists(fp) else 0
        mark = "·" if size else "✗"
        print(f"    [{mark}] {fp:<45} {size:>6} bytes")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    banner("SHADE — Secure Hospital And Document Exchange\n  Full Cryptographic Pipeline Demo")
    print()
    print("  Tasks covered : A (Symmetric) · B (Asymmetric/KE) ·")
    print("                  C (Integrity) · D (Authentication)")
    print("  Document      : patient_report.txt (EMR — Arjun Mehta)")
    print()

    phase_0_setup()
    phase_1_task_a()
    phase_2_task_b()
    phase_3_task_c()
    phase_4_task_d()
    phase_5_summary()

if __name__ == "__main__":
    main()
