"""
Full-pipeline runner (Phase 5). Calls the same core/ functions each card's
render function uses, in dependency order, and populates session_state
with the exact keys each CardSpec.produces declares -- so card_status()
correctly reports every card as "done" afterward without needing to
simulate a button click for each one.

Deliberately lives outside ui/cards/ since it isn't a renderer -- it's an
orchestrator, matching the CLI's original option 15 ("Run Complete
SHADE Pipeline").
"""

from core.asymmetric import generate_rsa_keypair, hybrid_encrypt_decrypt
from core.auth import generate_x509_certificate, simulate_kerberos, sign_and_verify
from core.image_modes import encrypt_bmp_pixels
from core.integrity import compute_sha256, tamper_bytes
from core.key_exchange import diffie_hellman_exchange, simulate_dh_mitm
from core.sample_data import get_sample_bmp, get_sample_report
from core.symmetric import encrypt_3des_cbc, encrypt_aes_cbc


def run_full_pipeline(ss) -> dict:
    """
    Runs every implemented card's underlying logic once, reusing whatever
    is already in session_state (e.g. a custom plaintext from the AES card)
    rather than overwriting it. Returns a dict of per-card pass/fail for
    callers that want it beyond what session_state now reflects.
    """
    results = {}
    plaintext = ss.get("aes_plaintext") or get_sample_report("default")

    # Layer 1 -- Symmetric Encryption
    if "aes_ciphertext" not in ss:
        aes = encrypt_aes_cbc(plaintext)
        ss["aes_key"], ss["aes_iv"] = aes["key"], aes["iv"]
        ss["aes_ciphertext"], ss["aes_plaintext"] = aes["ciphertext"], plaintext
    results["aes_cbc"] = True

    if "des_ciphertext" not in ss:
        des = encrypt_3des_cbc(plaintext)
        ss["des_key"], ss["des_iv"] = des["key"], des["iv"]
        ss["des_ciphertext"], ss["des_plaintext"] = des["ciphertext"], plaintext
    results["des_cbc"] = True

    if "avalanche_result" not in ss:
        from core.symmetric import compute_avalanche
        ss["avalanche_result"] = compute_avalanche(
            plaintext, key=ss["aes_key"], iv=ss["aes_iv"], byte_index=0, bit_mask=0x01
        )
    results["avalanche"] = True

    if "ecb_output_bmp" not in ss:
        bmp = get_sample_bmp()
        ecb = encrypt_bmp_pixels(bmp, mode="ECB")
        cbc = encrypt_bmp_pixels(bmp, key=ecb["key"], mode="CBC")
        ss["ecb_output_bmp"], ss["cbc_output_bmp"] = ecb["output_bmp"], cbc["output_bmp"]
    results["ecb_vs_cbc"] = True

    # Layer 2 -- Asymmetric & Key Exchange
    if "rsa_public_key" not in ss:
        rsa = generate_rsa_keypair()
        ss["rsa_private_key"], ss["rsa_public_key"] = rsa["private_key"], rsa["public_key"]
    results["rsa_keygen"] = True

    if "encrypted_aes_key" not in ss:
        hybrid = hybrid_encrypt_decrypt(
            plaintext, ss["aes_key"], ss["aes_iv"], ss["aes_ciphertext"],
            ss["rsa_public_key"], ss["rsa_private_key"],
        )
        ss["encrypted_aes_key"] = hybrid["encrypted_aes_key"]
        results["hybrid_encrypt"] = hybrid["match"]
    else:
        results["hybrid_encrypt"] = True

    if "dh_shared_secret" not in ss:
        dh = diffie_hellman_exchange()
        ss["dh_shared_secret"] = dh["shared_secret"]
        results["diffie_hellman"] = dh["match"]
    else:
        results["diffie_hellman"] = True

    if "mitm_secrets" not in ss:
        mitm = simulate_dh_mitm()
        ss["mitm_secrets"] = mitm
        results["mitm"] = mitm["attack_succeeded"]
    else:
        results["mitm"] = True

    # Layer 3 -- Integrity
    if "sha256_original" not in ss:
        ss["sha256_original"] = compute_sha256(plaintext)
    results["sha256_integrity"] = True

    if "tampered_ciphertext" not in ss:
        tamper = tamper_bytes(ss["aes_ciphertext"], [(10, 0xFF), (50, 0xAA)])
        ss["tampered_ciphertext"] = tamper["tampered"]
    results["tamper_detection"] = True

    # Layer 4 -- Authentication
    if "signature" not in ss:
        sig = sign_and_verify(plaintext, ss.get("rsa_private_key"))
        ss["signature"] = sig["signature"]
        results["digital_signature"] = sig["valid"] and sig["tamper_detected"]
    else:
        results["digital_signature"] = True

    if "sender_certificate" not in ss:
        cert = generate_x509_certificate(ss.get("rsa_private_key"))
        ss["sender_certificate"] = cert["certificate"]
        results["x509_cert"] = cert["valid"]
    else:
        results["x509_cert"] = True

    if "kerberos_stage" not in ss:
        krb = simulate_kerberos()
        ss["kerberos_stage"] = krb["ticket"]
        results["kerberos"] = krb["access_granted"]
    else:
        results["kerberos"] = True

    return results
