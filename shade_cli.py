"""
================================================================================
  SHADE — Secure Hospital And Document Exchange
  Interactive CLI Menu
================================================================================
  Run: python shade_cli.py
  Requires: pip install pycryptodome cryptography Pillow
================================================================================
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import os, sys, time, json, datetime, warnings

warnings.filterwarnings("ignore")

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from Crypto.Cipher      import AES, DES3
from Crypto.PublicKey    import RSA
from Crypto.Cipher      import PKCS1_OAEP
from Crypto.Signature   import pkcs1_15
from Crypto.Hash        import SHA256
from Crypto.Util.Padding import pad, unpad
from Crypto.Random      import get_random_bytes

from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives            import hashes, serialization
from cryptography                              import x509
from cryptography.x509.oid                    import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa

from PIL import Image, ImageDraw

# ── STATE ────────────────────────────────────────────────────────────────────
STATE = {
    # Setup
    "document_path"    : "patient_report.txt",
    "plaintext"        : None,

    # Layer 1 outputs
    "aes_key"          : None,
    "aes_iv"           : None,
    "aes_ciphertext"   : None,
    "des_key"          : None,
    "des_iv"           : None,
    "aes_done"         : False,
    "des_done"         : False,
    "avalanche_done"   : False,
    "ecb_cbc_done"     : False,
    "aes_detail"       : "",
    "des_detail"       : "",
    "avalanche_detail" : "",
    "ecb_cbc_detail"   : "",

    # Layer 2 outputs
    "receiver_priv"    : None,
    "receiver_pub"     : None,
    "enc_aes_key"      : None,
    "rsa_done"         : False,
    "hybrid_done"      : False,
    "dh_done"          : False,
    "mitm_done"        : False,
    "rsa_detail"       : "",
    "hybrid_detail"    : "",
    "dh_detail"        : "",
    "mitm_detail"      : "",

    # Layer 3 outputs
    "original_hash"    : None,
    "integrity_done"   : False,
    "tamper_done"      : False,
    "integrity_detail" : "",
    "tamper_detail"    : "",

    # Layer 4 outputs
    "sender_key"       : None,
    "sender_pub_pem"   : None,
    "signature"        : None,
    "sig_done"         : False,
    "verify_done"      : False,
    "cert_done"        : False,
    "kerberos_done"    : False,
    "sig_detail"       : "",
    "verify_detail"    : "",
    "cert_detail"      : "",
    "kerberos_detail"  : "",

    # Errors
    "failed"           : set(),
}

# ── Helper Functions ─────────────────────────────────────────────────────────
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def wait_for_enter():
    input("\n  Press Enter to return to menu...")

def status_icon(done_key):
    if done_key in STATE.get("failed", set()):
        return "❌"
    return "✅" if STATE.get(done_key, False) else "⬜"

def show_menu():
    clear_screen()
    doc_path = STATE["document_path"]
    doc_size = len(STATE["plaintext"]) if STATE["plaintext"] else 0

    print("╔══════════════════════════════════════════════════════╗")
    print("║     SHADE — Secure Hospital Document Exchange       ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  Document : {doc_path:<20} ({doc_size} bytes)     ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║                                                      ║")
    print("║  ── LAYER 1: SYMMETRIC ENCRYPTION ─────────────────  ║")
    print(f"║   1.  AES-128 CBC Encryption & Decryption    [{status_icon('aes_done')}]  ║")
    print(f"║   2.  3-DES CBC Encryption & Decryption      [{status_icon('des_done')}]  ║")
    print(f"║   3.  Avalanche Effect Analysis              [{status_icon('avalanche_done')}]  ║")
    print(f"║   4.  ECB vs CBC Image Comparison            [{status_icon('ecb_cbc_done')}]  ║")
    print("║                                                      ║")
    print("║  ── LAYER 2: ASYMMETRIC & KEY EXCHANGE ────────────  ║")
    print(f"║   5.  RSA-2048 Key Generation                [{status_icon('rsa_done')}]  ║")
    print(f"║   6.  Hybrid Envelope Encryption             [{status_icon('hybrid_done')}]  ║")
    print(f"║   7.  Diffie-Hellman Key Exchange             [{status_icon('dh_done')}]  ║")
    print(f"║   8.  MITM Attack Simulation                 [{status_icon('mitm_done')}]  ║")
    print("║                                                      ║")
    print("║  ── LAYER 3: INTEGRITY ────────────────────────────  ║")
    print(f"║   9.  SHA-256 Integrity Verification         [{status_icon('integrity_done')}]  ║")
    print(f"║  10.  Ciphertext Tamper Detection             [{status_icon('tamper_done')}]  ║")
    print("║                                                      ║")
    print("║  ── LAYER 4: AUTHENTICATION ───────────────────────  ║")
    print(f"║  11.  RSA Digital Signature (Sign)            [{status_icon('sig_done')}]  ║")
    print(f"║  12.  Signature Verification                 [{status_icon('verify_done')}]  ║")
    print(f"║  13.  X.509 Certificate Generation           [{status_icon('cert_done')}]  ║")
    print(f"║  14.  Kerberos Authentication Simulation     [{status_icon('kerberos_done')}]  ║")
    print("║                                                      ║")
    print("║  ── FULL PIPELINE ─────────────────────────────────  ║")
    print("║  15.  ▶ Run Complete SHADE Pipeline                  ║")
    print("║  16.  📋 Show Results Summary                        ║")
    print("║  17.  🔄 Reset All (start fresh)                     ║")
    print("║                                                      ║")
    print("║   0.  Exit                                           ║")
    print("║                                                      ║")
    print("╚══════════════════════════════════════════════════════╝")

def check_dependency(needs):
    """
    needs: list of tuples (state_key, human_label, option_number)
    Returns True if all dependencies met, False otherwise (prints warning).
    """
    missing = []
    for key, label, opt_num in needs:
        if not STATE.get(key, False):
            missing.append((label, opt_num))
    if missing:
        print("  ⚠️  This step has unmet dependencies:\n")
        for label, opt_num in missing:
            print(f"     → Option {opt_num}: {label}")
        print(f"\n  Run the above option(s) first, then come back to this.")
        return False
    return True

# ── LAYER 1 FUNCTIONS ────────────────────────────────────────────────────────

def cmd_aes_encrypt(silent=False):
    if not silent:
        print_header("AES-128 CBC Encryption & Decryption")

    plaintext = STATE["plaintext"]

    # Generate key and IV
    aes_key = get_random_bytes(16)
    aes_iv  = get_random_bytes(16)
    with open("key.bin", "wb") as f: f.write(aes_key)
    with open("iv.bin",  "wb") as f: f.write(aes_iv)
    print(f"  [·] Generated AES-128 key : {aes_key.hex()}")
    print(f"  [·] Generated IV          : {aes_iv.hex()}")

    # Encrypt
    cipher     = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16))
    with open("patient_report_AES_encrypted.bin", "wb") as f:
        f.write(ciphertext)
    print(f"  [·] Ciphertext size       : {len(ciphertext)} bytes")

    # Decrypt and verify
    cipher_d  = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    decrypted = unpad(cipher_d.decrypt(ciphertext), 16)
    with open("patient_report_AES_decrypted.txt", "wb") as f:
        f.write(decrypted)

    if decrypted == plaintext:
        detail = f"{len(plaintext)}B → {len(ciphertext)}B cipher → recovered"
        print(f"\n  [✅] AES-128 CBC Encryption — {detail}")
        STATE["aes_detail"] = detail
    else:
        print(f"\n  [❌] AES-128 CBC Encryption — decryption mismatch!")
        STATE["failed"].add("aes_done")

    # Timing benchmark
    print(f"\n  {'File Size':<10} {'AES-128 (ms)':<16} {'Speedup vs 3-DES'}")
    print(f"  {'─'*10} {'─'*15} {'─'*16}")
    des_key_bench = get_random_bytes(24)
    des_iv_bench  = get_random_bytes(8)
    sizes = {"1 KB": 1_024, "100 KB": 102_400, "1 MB": 1_048_576}
    for label, sz in sizes.items():
        sample = os.urandom(sz)
        t0 = time.perf_counter()
        AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(sample, 16))
        aes_t = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        DES3.new(des_key_bench, DES3.MODE_CBC, des_iv_bench).encrypt(pad(sample, 8))
        des_t = (time.perf_counter() - t0) * 1000
        print(f"  {label:<10} {aes_t:<16.4f} ~{des_t/aes_t:.1f}x faster (AES)")

    # Store in STATE
    STATE["aes_key"]        = aes_key
    STATE["aes_iv"]         = aes_iv
    STATE["aes_ciphertext"] = ciphertext
    STATE["aes_done"]       = True

    if not silent:
        wait_for_enter()


def cmd_3des_encrypt(silent=False):
    if not silent:
        print_header("3-DES CBC Encryption & Decryption")

    plaintext = STATE["plaintext"]

    des_key = get_random_bytes(24)
    des_iv  = get_random_bytes(8)
    print(f"  [·] Generated 3-DES key (24B) : {des_key.hex()[:32]}...")
    print(f"  [·] Generated IV (8B)          : {des_iv.hex()}")

    # Encrypt
    cipher3 = DES3.new(des_key, DES3.MODE_CBC, des_iv)
    ct3     = cipher3.encrypt(pad(plaintext, 8))
    with open("patient_report_3DES_encrypted.bin", "wb") as f:
        f.write(ct3)
    print(f"  [·] Ciphertext size            : {len(ct3)} bytes")

    # Decrypt and verify
    cipher3d = DES3.new(des_key, DES3.MODE_CBC, des_iv)
    dec3     = unpad(cipher3d.decrypt(ct3), 8)
    with open("patient_report_3DES_decrypted.txt", "wb") as f:
        f.write(dec3)

    if dec3 == plaintext:
        detail = f"{len(plaintext)}B → {len(ct3)}B cipher → recovered"
        print(f"\n  [✅] 3-DES CBC Encryption — {detail}")
        STATE["des_detail"] = detail
    else:
        print(f"\n  [❌] 3-DES CBC Encryption — decryption mismatch!")
        STATE["failed"].add("des_done")

    # Timing
    print(f"\n  {'File Size':<10} {'3-DES (ms)':<16}")
    print(f"  {'─'*10} {'─'*15}")
    sizes = {"1 KB": 1_024, "100 KB": 102_400, "1 MB": 1_048_576}
    for label, sz in sizes.items():
        sample = os.urandom(sz)
        t0 = time.perf_counter()
        DES3.new(des_key, DES3.MODE_CBC, des_iv).encrypt(pad(sample, 8))
        des_t = (time.perf_counter() - t0) * 1000
        print(f"  {label:<10} {des_t:<16.4f}")

    STATE["des_key"]  = des_key
    STATE["des_iv"]   = des_iv
    STATE["des_done"] = True

    if not silent:
        wait_for_enter()


def cmd_avalanche(silent=False):
    if not silent:
        print_header("Avalanche Effect Analysis")

    if not check_dependency([("aes_done", "AES-128 CBC Encryption", 1)]):
        if not silent:
            wait_for_enter()
        return

    plaintext = STATE["plaintext"]
    aes_key   = STATE["aes_key"]
    aes_iv    = STATE["aes_iv"]

    modified = bytearray(plaintext)
    modified[0] ^= 0x01
    modified = bytes(modified)

    print(f"  [·] Original byte 0  : 0b{plaintext[0]:08b}")
    print(f"  [·] Modified byte 0  : 0b{modified[0]:08b}  (1 bit flipped via ^= 0x01)")

    ct_orig = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(plaintext, 16))
    ct_mod  = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(modified, 16))

    length     = min(len(ct_orig), len(ct_mod))
    diff_bits  = sum(bin(ct_orig[i] ^ ct_mod[i]).count('1') for i in range(length))
    total_bits = length * 8
    pct        = diff_bits / total_bits * 100

    print(f"\n  [·] Total bits tested     : {total_bits:,}")
    print(f"  [·] Bits changed          : {diff_bits:,}")
    print(f"  [·] Avalanche percentage  : {pct:.2f}%")
    print(f"  [·] Ideal range           : 45% – 55%")

    if 45 <= pct <= 55:
        detail = f"{diff_bits}/{total_bits} bits → {pct:.2f}%"
        print(f"\n  [✅] Avalanche Effect — {detail}")
        STATE["avalanche_detail"] = detail
    else:
        print(f"\n  [❌] Avalanche Effect — {pct:.2f}% outside ideal range!")
        STATE["failed"].add("avalanche_done")

    STATE["avalanche_done"] = True

    if not silent:
        wait_for_enter()


def cmd_ecb_vs_cbc(silent=False):
    if not silent:
        print_header("ECB vs CBC Image Comparison")

    # Generate test image
    img = Image.new("RGB", (256, 256), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 215, 215], fill="blue")
    draw.rectangle([80, 80, 175, 175], fill="white")
    draw.rectangle([100, 100, 155, 155], fill="blue")
    img.save("sample.bmp")
    print(f"  [·] Generated sample.bmp (256×256 RGB)")

    with open("sample.bmp", "rb") as f:
        header     = f.read(54)
        pixel_data = f.read()

    img_key = get_random_bytes(16)
    img_iv  = get_random_bytes(16)
    padded  = pad(pixel_data, 16)

    # ECB
    ecb_enc = AES.new(img_key, AES.MODE_ECB).encrypt(padded)[:len(pixel_data)]
    with open("ecb_output.bmp", "wb") as f: f.write(header + ecb_enc)
    print(f"  [·] ECB encrypted → ecb_output.bmp  (pattern leakage visible)")

    # CBC
    cbc_enc = AES.new(img_key, AES.MODE_CBC, img_iv).encrypt(padded)[:len(pixel_data)]
    with open("cbc_output.bmp", "wb") as f: f.write(header + cbc_enc)
    print(f"  [·] CBC encrypted → cbc_output.bmp  (pseudo-random noise)")

    detail = "3 files saved"
    print(f"\n  [✅] ECB vs CBC Image — {detail}")
    STATE["ecb_cbc_detail"] = detail
    STATE["ecb_cbc_done"]   = True

    if not silent:
        wait_for_enter()

# ── LAYER 2 FUNCTIONS ────────────────────────────────────────────────────────

def cmd_rsa_keygen(silent=False):
    if not silent:
        print_header("RSA-2048 Key Generation")

    print(f"  [·] Generating 2048-bit RSA key pair for Receiver...")
    rsa_key  = RSA.generate(2048)
    priv_pem = rsa_key.export_key()
    pub_pem  = rsa_key.publickey().export_key()
    with open("receiver_private.pem", "wb") as f: f.write(priv_pem)
    with open("receiver_public.pem",  "wb") as f: f.write(pub_pem)

    print(f"  [·] receiver_private.pem : {len(priv_pem)} bytes")
    print(f"  [·] receiver_public.pem  : {len(pub_pem)} bytes")
    print(f"  [·] Key size             : {rsa_key.size_in_bits()} bits")
    print(f"  [·] Public exponent (e)  : {rsa_key.e}")

    detail = f"private ({len(priv_pem)}B) + public ({len(pub_pem)}B)"
    print(f"\n  [✅] RSA-2048 Key Generation — {detail}")

    STATE["receiver_priv"] = priv_pem
    STATE["receiver_pub"]  = pub_pem
    STATE["rsa_detail"]    = "2048-bit"
    STATE["rsa_done"]      = True

    if not silent:
        wait_for_enter()


def cmd_hybrid_encrypt(silent=False):
    if not silent:
        print_header("Hybrid Envelope Encryption")

    if not check_dependency([
        ("aes_done", "AES-128 CBC Encryption", 1),
        ("rsa_done", "RSA-2048 Key Generation", 5),
    ]):
        if not silent:
            wait_for_enter()
        return

    plaintext  = STATE["plaintext"]
    aes_key    = STATE["aes_key"]
    aes_iv     = STATE["aes_iv"]
    ciphertext = STATE["aes_ciphertext"]
    pub_pem    = STATE["receiver_pub"]
    priv_pem   = STATE["receiver_priv"]

    # Sender wraps AES key with RSA-OAEP
    print(f"  [·] Sender encrypts AES key with RSA-OAEP...")
    pub_key     = RSA.import_key(pub_pem)
    cipher_rsa  = PKCS1_OAEP.new(pub_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)
    with open("encrypted_aes_key.bin", "wb") as f: f.write(enc_aes_key)
    print(f"  [·] encrypted_aes_key.bin : {len(enc_aes_key)} bytes (RSA ciphertext)")

    # Receiver unwraps and recovers document
    print(f"  [·] Receiver decrypts envelope and recovers document...")
    priv_key       = RSA.import_key(priv_pem)
    cipher_rsa_d   = PKCS1_OAEP.new(priv_key)
    recovered_key  = cipher_rsa_d.decrypt(enc_aes_key)
    cipher_d       = AES.new(recovered_key, AES.MODE_CBC, aes_iv)
    recovered_doc  = unpad(cipher_d.decrypt(ciphertext), 16)
    with open("patient_report_hybrid_decrypted.txt", "wb") as f:
        f.write(recovered_doc)

    if recovered_doc == plaintext:
        detail = f"{len(enc_aes_key)}B envelope"
        print(f"\n  [✅] Hybrid Envelope Encryption — AES key wrapped → unwrapped → document recovered")
        STATE["hybrid_detail"] = detail
    else:
        print(f"\n  [❌] Hybrid Envelope Encryption — document mismatch!")
        STATE["failed"].add("hybrid_done")

    STATE["enc_aes_key"]  = enc_aes_key
    STATE["hybrid_done"]  = True

    if not silent:
        wait_for_enter()


def cmd_diffie_hellman(silent=False):
    if not silent:
        print_header("Diffie-Hellman Key Exchange")

    print(f"  [·] Generating DH parameters (512-bit, g=2)...")
    params      = dh.generate_parameters(generator=2, key_size=512)
    sender_priv = params.generate_private_key()
    recv_priv   = params.generate_private_key()
    sender_pub  = sender_priv.public_key()
    recv_pub    = recv_priv.public_key()

    print(f"  [·] Sender  public key (A) : {sender_pub.public_numbers().y}")
    print(f"  [·] Receiver public key (B): {recv_pub.public_numbers().y}")

    sender_shared   = sender_priv.exchange(recv_pub)
    receiver_shared = recv_priv.exchange(sender_pub)

    print(f"\n  [·] Sender  shared secret  : {sender_shared.hex()[:32]}...")
    print(f"  [·] Receiver shared secret : {receiver_shared.hex()[:32]}...")

    # Store params for MITM reuse
    STATE["_dh_params"]      = params
    STATE["_dh_sender_priv"] = sender_priv
    STATE["_dh_recv_priv"]   = recv_priv
    STATE["_dh_sender_pub"]  = sender_pub
    STATE["_dh_recv_pub"]    = recv_pub

    if sender_shared == receiver_shared:
        detail = "match ✓"
        print(f"\n  [✅] Diffie-Hellman Key Exchange — shared secrets match!")
        STATE["dh_detail"] = detail
    else:
        print(f"\n  [❌] Diffie-Hellman Key Exchange — secrets do NOT match!")
        STATE["failed"].add("dh_done")

    STATE["dh_done"] = True

    if not silent:
        wait_for_enter()


def cmd_mitm_attack(silent=False):
    if not silent:
        print_header("Man-In-The-Middle (MITM) Attack Simulation")

    # MITM runs its own independent DH — no dependency needed
    print(f"  [·] Generating fresh DH parameters for MITM demo...")
    params      = dh.generate_parameters(generator=2, key_size=512)
    sender_priv = params.generate_private_key()
    recv_priv   = params.generate_private_key()
    sender_pub  = sender_priv.public_key()
    recv_pub    = recv_priv.public_key()

    mallory_priv = params.generate_private_key()
    mallory_pub  = mallory_priv.public_key()

    print(f"  [!] Mallory intercepts Sender's public key (A) → substitutes her own")
    print(f"  [!] Mallory intercepts Receiver's public key (B) → substitutes her own")

    sender_thinks   = sender_priv.exchange(mallory_pub)
    receiver_thinks = recv_priv.exchange(mallory_pub)
    mallory_s       = mallory_priv.exchange(sender_pub)
    mallory_r       = mallory_priv.exchange(recv_pub)

    print(f"\n  Sender  believes secret  : {sender_thinks.hex()[:24]}...")
    print(f"  Mallory↔Sender  secret   : {mallory_s.hex()[:24]}...")
    print(f"  Receiver believes secret : {receiver_thinks.hex()[:24]}...")
    print(f"  Mallory↔Receiver secret  : {mallory_r.hex()[:24]}...")

    if sender_thinks == mallory_s and receiver_thinks == mallory_r:
        detail = "attack proved"
        print(f"\n  [✅] MITM Simulation — Sender & Receiver hold different secrets!")
        print(f"  [!] Prevention: Authenticated DH (X.509 certs / TLS / PKI)")
        STATE["mitm_detail"] = detail
    else:
        print(f"\n  [❌] MITM Simulation — unexpected result!")
        STATE["failed"].add("mitm_done")

    STATE["mitm_done"] = True

    if not silent:
        wait_for_enter()

# ── LAYER 3 FUNCTIONS ────────────────────────────────────────────────────────

def cmd_sha256_check(silent=False):
    if not silent:
        print_header("SHA-256 Integrity Verification")

    if not check_dependency([("aes_done", "AES-128 CBC Encryption", 1)]):
        if not silent:
            wait_for_enter()
        return

    plaintext  = STATE["plaintext"]
    aes_key    = STATE["aes_key"]
    aes_iv     = STATE["aes_iv"]
    ciphertext = STATE["aes_ciphertext"]

    # Sender computes hash
    original_hash = SHA256.new(plaintext).hexdigest()
    with open("original_hash.txt", "w") as f: f.write(original_hash)
    print(f"  [·] Original SHA-256 : {original_hash}")

    # Receiver decrypts and verifies
    decrypted     = unpad(AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(ciphertext), 16)
    received_hash = SHA256.new(decrypted).hexdigest()
    print(f"  [·] Received SHA-256 : {received_hash}")

    if original_hash == received_hash:
        detail = "hashes match"
        print(f"\n  [✅] SHA-256 Integrity Check — hashes match, document untampered!")
        STATE["integrity_detail"] = detail
    else:
        print(f"\n  [❌] SHA-256 Integrity Check — hash mismatch!")
        STATE["failed"].add("integrity_done")

    STATE["original_hash"]  = original_hash
    STATE["integrity_done"] = True

    if not silent:
        wait_for_enter()


def cmd_tamper_detect(silent=False):
    if not silent:
        print_header("Ciphertext Tamper Detection")

    if not check_dependency([
        ("aes_done",       "AES-128 CBC Encryption",       1),
        ("integrity_done", "SHA-256 Integrity Verification", 9),
    ]):
        if not silent:
            wait_for_enter()
        return

    aes_key       = STATE["aes_key"]
    aes_iv        = STATE["aes_iv"]
    ciphertext    = STATE["aes_ciphertext"]
    original_hash = STATE["original_hash"]

    # Tamper ciphertext
    tampered = bytearray(ciphertext)
    tampered[10] ^= 0xFF
    tampered[50] ^= 0xAA
    tampered = bytes(tampered)
    with open("patient_report_TAMPERED.bin", "wb") as f: f.write(tampered)

    print(f"  [!] Simulating in-transit tampering:")
    print(f"      Byte 10: XOR 0xFF")
    print(f"      Byte 50: XOR 0xAA")

    try:
        dec_tampered  = unpad(AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(tampered), 16)
        tampered_hash = SHA256.new(dec_tampered).hexdigest()
    except Exception:
        tampered_hash = "PADDING_ERROR_" + get_random_bytes(8).hex()

    print(f"\n  Expected (original)  : {original_hash}")
    print(f"  Calculated (tampered): {tampered_hash}")

    if original_hash != tampered_hash:
        detail = "alert raised"
        print(f"\n  [✅] Tamper Detection — hash mismatch alert triggered!")
        print(f"  [🚨] Corrupted file immediately rejected.")
        STATE["tamper_detail"] = detail
    else:
        print(f"\n  [❌] Tamper Detection — tampered hash unexpectedly matched!")
        STATE["failed"].add("tamper_done")

    STATE["tamper_done"] = True

    if not silent:
        wait_for_enter()

# ── LAYER 4 FUNCTIONS ────────────────────────────────────────────────────────

def cmd_digital_signature(silent=False):
    if not silent:
        print_header("RSA Digital Signature (Sign)")

    if not check_dependency([("integrity_done", "SHA-256 Integrity Verification", 9)]):
        if not silent:
            wait_for_enter()
        return

    plaintext = STATE["plaintext"]

    # Generate sender key pair
    print(f"  [·] Generating RSA-2048 key pair for Sender (Dr. Kavya Sharma)...")
    sender_key      = RSA.generate(2048)
    sender_priv_pem = sender_key.export_key()
    sender_pub_pem  = sender_key.publickey().export_key()
    with open("sender_private.pem", "wb") as f: f.write(sender_priv_pem)
    with open("sender_public.pem",  "wb") as f: f.write(sender_pub_pem)
    print(f"  [·] sender_private.pem : {len(sender_priv_pem)} bytes")
    print(f"  [·] sender_public.pem  : {len(sender_pub_pem)} bytes")

    # Sign
    print(f"  [·] Signing SHA-256 hash with Sender's private key...")
    h         = SHA256.new(plaintext)
    signer    = pkcs1_15.new(sender_key)
    signature = signer.sign(h)
    with open("document_signature.bin", "wb") as f: f.write(signature)

    print(f"\n  SHA-256 hash   : {h.hexdigest()}")
    print(f"  Signature (hex): {signature.hex()[:32]}...")
    print(f"  Signature size : {len(signature)} bytes")

    detail = f"{len(signature)}B signature"
    print(f"\n  [✅] Digital Signature — document signed with RSA PKCS#1 v1.5")

    STATE["sender_key"]     = sender_key
    STATE["sender_pub_pem"] = sender_pub_pem
    STATE["signature"]      = signature
    STATE["sig_detail"]     = detail
    STATE["sig_done"]       = True

    if not silent:
        wait_for_enter()


def cmd_verify_signature(silent=False):
    if not silent:
        print_header("Signature Verification")

    if not check_dependency([("sig_done", "RSA Digital Signature (Sign)", 11)]):
        if not silent:
            wait_for_enter()
        return

    plaintext      = STATE["plaintext"]
    sender_pub_pem = STATE["sender_pub_pem"]
    signature      = STATE["signature"]

    # Verify valid signature
    print(f"  [·] Receiver verifies signature using Sender's public key...")
    pub_key  = RSA.import_key(sender_pub_pem)
    verifier = pkcs1_15.new(pub_key)
    try:
        verifier.verify(SHA256.new(plaintext), signature)
        print(f"  [✅] Signature VALID — document authentic, sender confirmed")
        valid = True
    except (ValueError, TypeError):
        print(f"  [❌] Signature verification failed!")
        valid = False

    # Tamper test
    print(f"\n  [·] Tamper test — modifying one byte of document...")
    tampered_doc = bytearray(plaintext)
    tampered_doc[0] ^= 0x01
    try:
        verifier.verify(SHA256.new(bytes(tampered_doc)), signature)
        print(f"  [❌] Tampered document incorrectly accepted!")
        tamper_caught = False
    except (ValueError, TypeError):
        print(f"  [✅] Tampered document correctly rejected!")
        tamper_caught = True

    if valid and tamper_caught:
        detail = "verified + tamper rejected"
        STATE["verify_detail"] = detail
    else:
        STATE["failed"].add("verify_done")

    STATE["verify_done"] = True

    if not silent:
        wait_for_enter()


def cmd_x509_cert(silent=False):
    if not silent:
        print_header("X.509 Certificate Generation")

    print(f"  [·] Generating X.509 self-signed certificate for Sender...")
    cert_key = crypto_rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME,           "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Gujarat"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME,      "SHADE Hospital Network"),
        x509.NameAttribute(NameOID.COMMON_NAME,            "Dr. Sender"),
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

    # Parse and display
    loaded = x509.load_pem_x509_certificate(cert_pem)
    print(f"\n  Subject    : {loaded.subject.rfc4514_string()}")
    print(f"  Issuer     : {loaded.issuer.rfc4514_string()}")
    print(f"  Valid From : {loaded.not_valid_before_utc.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Valid Until: {loaded.not_valid_after_utc.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Key Size   : {loaded.public_key().key_size} bits")
    print(f"  Sig Algo   : SHA256withRSA")
    print(f"  Cert File  : sender_certificate.pem ({len(cert_pem)} bytes)")

    if loaded.not_valid_before_utc <= now <= loaded.not_valid_after_utc:
        detail = "self-signed, valid"
        print(f"\n  [✅] X.509 Certificate — self-signed, parsed, within validity period")
        STATE["cert_detail"] = detail
    else:
        print(f"\n  [❌] X.509 Certificate — date validation failed!")
        STATE["failed"].add("cert_done")

    STATE["cert_done"] = True

    if not silent:
        wait_for_enter()


def cmd_kerberos(silent=False):
    if not silent:
        print_header("Kerberos Authentication Simulation")

    client_name  = "Dr. Sender"
    service_name = "HospitalRecordServer"

    as_key  = get_random_bytes(16)
    tgs_key = get_random_bytes(16)
    svc_key = get_random_bytes(16)

    def aes_encrypt_data(key, data_dict):
        raw = json.dumps(data_dict).encode()
        iv  = get_random_bytes(16)
        ct  = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(raw, 16))
        return iv + ct

    def aes_decrypt_data(key, blob):
        iv, ct = blob[:16], blob[16:]
        raw    = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
        return json.loads(raw.decode())

    expiry = (datetime.datetime.now(datetime.timezone.utc)
              + datetime.timedelta(hours=8)).isoformat()

    # Step 1 & 2 — Client ↔ AS
    print(f"  [1] {client_name} → AS : requesting authentication")
    tgt_payload = {"client": client_name, "session_key": tgs_key.hex(), "expires": expiry}
    tgt_blob    = aes_encrypt_data(as_key, tgt_payload)
    print(f"  [2] AS → {client_name} : TGT issued ({len(tgt_blob)}B, encrypted with AS key)")

    # Step 3 & 4 — Client ↔ TGS
    print(f"  [3] {client_name} → TGS : submitting TGT, requesting ticket for '{service_name}'")
    tgt_decrypted = aes_decrypt_data(as_key, tgt_blob)
    assert tgt_decrypted["client"] == client_name
    st_payload = {"client": client_name, "service": service_name,
                  "session_key": svc_key.hex(), "expires": expiry}
    st_blob    = aes_encrypt_data(tgs_key, st_payload)
    print(f"  [4] TGS → {client_name} : Service Ticket issued ({len(st_blob)}B) for '{service_name}'")

    # Step 5 — Client → Service
    print(f"  [5] {client_name} → {service_name} : presenting Service Ticket")
    st_decrypted = aes_decrypt_data(tgs_key, st_blob)
    assert st_decrypted["service"] == service_name
    print(f"      Authorized client : {st_decrypted['client']}")
    print(f"      Target service    : {st_decrypted['service']}")
    print(f"      Ticket expires    : {st_decrypted['expires']}")

    detail = f"TGT({len(tgt_blob)}B) → ST({len(st_blob)}B)"
    print(f"\n  [✅] Kerberos Authentication — {detail} → access granted")

    STATE["kerberos_detail"] = detail
    STATE["kerberos_done"]   = True

    if not silent:
        wait_for_enter()

# ── FULL PIPELINE ────────────────────────────────────────────────────────────

def cmd_run_all(silent=False):
    if not silent:
        print_header("▶ Running Complete SHADE Pipeline")

    steps = [
        (" 1. AES-128 CBC Encryption",         cmd_aes_encrypt),
        (" 2. 3-DES CBC Encryption",            cmd_3des_encrypt),
        (" 3. Avalanche Effect",                cmd_avalanche),
        (" 4. ECB vs CBC Image",                cmd_ecb_vs_cbc),
        (" 5. RSA Key Generation",              cmd_rsa_keygen),
        (" 6. Hybrid Encryption",               cmd_hybrid_encrypt),
        (" 7. Diffie-Hellman",                  cmd_diffie_hellman),
        (" 8. MITM Attack",                     cmd_mitm_attack),
        (" 9. SHA-256 Integrity",               cmd_sha256_check),
        ("10. Tamper Detection",                cmd_tamper_detect),
        ("11. Digital Signature",               cmd_digital_signature),
        ("12. Signature Verification",          cmd_verify_signature),
        ("13. X.509 Certificate",               cmd_x509_cert),
        ("14. Kerberos Authentication",         cmd_kerberos),
    ]

    for label, func in steps:
        print(f"\n  {'─' * 56}")
        print(f"  Running: {label}...")
        print(f"  {'─' * 56}")
        func(silent=True)

    # Show summary at the end
    cmd_show_summary(silent=True)

    if not silent:
        wait_for_enter()


def cmd_show_summary(silent=False):
    if not silent:
        clear_screen()

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║              SHADE PIPELINE — SESSION RESULTS              ║")
    print("╠══════════════════════════════════════════════════════════════╣")

    checks = [
        ("AES-128 CBC Encryption",     "aes_done",       "aes_detail"),
        ("3-DES CBC Encryption",       "des_done",       "des_detail"),
        ("Avalanche Effect",           "avalanche_done", "avalanche_detail"),
        ("ECB vs CBC Image",           "ecb_cbc_done",   "ecb_cbc_detail"),
        ("RSA-2048 Key Generation",    "rsa_done",       "rsa_detail"),
        ("Hybrid Envelope Encryption", "hybrid_done",    "hybrid_detail"),
        ("Diffie-Hellman Key Exchange", "dh_done",        "dh_detail"),
        ("MITM Simulation",            "mitm_done",      "mitm_detail"),
        ("SHA-256 Integrity Check",    "integrity_done", "integrity_detail"),
        ("Tamper Detection",           "tamper_done",     "tamper_detail"),
        ("Digital Signature",          "sig_done",        "sig_detail"),
        ("Signature Verification",     "verify_done",     "verify_detail"),
        ("X.509 Certificate",          "cert_done",       "cert_detail"),
        ("Kerberos Authentication",    "kerberos_done",   "kerberos_detail"),
    ]

    print(f"║  {'Check':<30} {'Status':<8} {'Detail':<18}  ║")
    print(f"║  {'─'*30} {'─'*7} {'─'*18}  ║")

    passed = 0
    failed = 0
    skipped = 0

    for label, done_key, detail_key in checks:
        if done_key in STATE.get("failed", set()):
            status = "❌ FAIL"
            detail = "error"
            failed += 1
        elif STATE.get(done_key, False):
            status = "✅ PASS"
            detail = STATE.get(detail_key, "") or "done"
            passed += 1
        else:
            status = "⬜ SKIP"
            detail = "not run yet"
            skipped += 1
        print(f"║  {label:<30} {status:<8} {detail:<18}  ║")

    total = len(checks)
    print(f"║  {'─'*30} {'─'*7} {'─'*18}  ║")
    print(f"║  Total: {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} failed", end="")
    if skipped:
        print(f", {skipped} skipped", end="")
    print(f"{'':>{42 - len(str(passed)) - len(str(total))}}║")
    print("╚══════════════════════════════════════════════════════════════╝")

    if passed == total:
        print("\n  🔒 All checks passed. SHADE pipeline complete!\n")
    elif failed:
        print(f"\n  ⚠️  {failed} check(s) failed. Review output above.\n")

    if not silent:
        wait_for_enter()


def cmd_reset(silent=False):
    if not silent:
        confirm = input("  ⚠️  Reset all state? This clears all keys and results. (y/n): ").strip()
        if confirm.lower() != 'y':
            print("  Cancelled.")
            wait_for_enter()
            return

    # Preserve document_path and plaintext
    doc_path  = STATE["document_path"]
    plaintext = STATE["plaintext"]

    # Reset all keys
    for key in list(STATE.keys()):
        if key.endswith("_done"):
            STATE[key] = False
        elif key.endswith("_detail"):
            STATE[key] = ""
        elif key == "failed":
            STATE[key] = set()
        elif key not in ("document_path", "plaintext"):
            STATE[key] = None

    STATE["document_path"] = doc_path
    STATE["plaintext"]     = plaintext

    print("  ✅ Reset complete — fresh session started")

    if not silent:
        wait_for_enter()

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    doc_path = "patient_report.txt"
    if not os.path.exists(doc_path):
        print(f"  ❌ {doc_path} not found. Place it next to shade_cli.py")
        return

    with open(doc_path, "rb") as f:
        STATE["plaintext"] = f.read()

    print(f"\n  🏥 SHADE CLI loaded — {doc_path} ({len(STATE['plaintext'])} bytes)")

    dispatch = {
        "1":  cmd_aes_encrypt,
        "2":  cmd_3des_encrypt,
        "3":  cmd_avalanche,
        "4":  cmd_ecb_vs_cbc,
        "5":  cmd_rsa_keygen,
        "6":  cmd_hybrid_encrypt,
        "7":  cmd_diffie_hellman,
        "8":  cmd_mitm_attack,
        "9":  cmd_sha256_check,
        "10": cmd_tamper_detect,
        "11": cmd_digital_signature,
        "12": cmd_verify_signature,
        "13": cmd_x509_cert,
        "14": cmd_kerberos,
        "15": cmd_run_all,
        "16": cmd_show_summary,
        "17": cmd_reset,
    }

    while True:
        show_menu()
        choice = input("  Choose option: ").strip()

        if choice == "0":
            print("\n  Goodbye. Stay secure. 🔒\n")
            break
        elif choice in dispatch:
            dispatch[choice]()
        else:
            print("  ❌ Invalid option. Try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()
