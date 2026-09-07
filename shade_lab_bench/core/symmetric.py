"""
Symmetric encryption primitives: AES-128-CBC, 3-DES-CBC, timing benchmarks,
and the avalanche-effect measurement.

No streamlit imports here -- see claude.md ground rule #3. Every public
function returns a dict with named keys; nothing is written to disk or
printed.
"""

import time

from Crypto.Cipher import AES, DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


# ---------------------------------------------------------------------------
# AES-128-CBC
# ---------------------------------------------------------------------------

def generate_aes_key() -> bytes:
    return get_random_bytes(16)


def generate_iv() -> bytes:
    return get_random_bytes(16)


def encrypt_aes_cbc(plaintext: bytes, key: bytes = None, iv: bytes = None) -> dict:
    key = key or generate_aes_key()
    iv = iv or generate_iv()
    start = time.perf_counter()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"ciphertext": ciphertext, "key": key, "iv": iv, "elapsed_ms": elapsed_ms}


def decrypt_aes_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> dict:
    start = time.perf_counter()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"plaintext": plaintext, "elapsed_ms": elapsed_ms}


# ---------------------------------------------------------------------------
# 3-DES-CBC
# ---------------------------------------------------------------------------

def generate_3des_key() -> bytes:
    return DES3.adjust_key_parity(get_random_bytes(24))


def encrypt_3des_cbc(plaintext: bytes, key: bytes = None, iv: bytes = None) -> dict:
    key = key or generate_3des_key()
    iv = iv or get_random_bytes(8)
    start = time.perf_counter()
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, DES3.block_size))
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"ciphertext": ciphertext, "key": key, "iv": iv, "elapsed_ms": elapsed_ms}


def decrypt_3des_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> dict:
    start = time.perf_counter()
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"plaintext": plaintext, "elapsed_ms": elapsed_ms}


# ---------------------------------------------------------------------------
# Benchmark helper -- shared by both AES and 3-DES cards
# ---------------------------------------------------------------------------

def benchmark_cipher(encrypt_fn, datasets: dict) -> dict:
    """
    datasets: {"1 KB": bytes, "100 KB": bytes, "1 MB": bytes}
    encrypt_fn: a function like encrypt_aes_cbc taking (plaintext) -> dict with elapsed_ms
    Returns: {"1 KB": elapsed_ms, "100 KB": elapsed_ms, "1 MB": elapsed_ms}
    """
    results = {}
    for label, data in datasets.items():
        results[label] = encrypt_fn(data)["elapsed_ms"]
    return results


# ---------------------------------------------------------------------------
# Avalanche effect
# ---------------------------------------------------------------------------

def compute_avalanche(plaintext: bytes, key: bytes = None, iv: bytes = None,
                       byte_index: int = 0, bit_mask: int = 0x01) -> dict:
    """
    Flips one bit in plaintext at byte_index (via XOR with bit_mask), encrypts
    both the original and modified plaintext with the SAME key/iv, and measures
    what fraction of ciphertext bits differ.

    Returns: {
        "original_ciphertext": bytes, "modified_ciphertext": bytes,
        "diff_bits": list[int] (bit positions that differ, for heatmap rendering),
        "bits_flipped": int, "total_bits": int, "percentage": float,
        "key": bytes, "iv": bytes,
    }
    """
    key = key or generate_aes_key()
    iv = iv or generate_iv()
    byte_index = min(byte_index, len(plaintext) - 1) if plaintext else 0

    modified = bytearray(plaintext)
    if modified:
        modified[byte_index] ^= bit_mask
    modified = bytes(modified)

    original_result = encrypt_aes_cbc(plaintext, key=key, iv=iv)
    modified_result = encrypt_aes_cbc(modified, key=key, iv=iv)

    c1 = original_result["ciphertext"]
    c2 = modified_result["ciphertext"]

    total_bits = len(c1) * 8
    diff_bits = []
    bits_flipped = 0
    for i, (b1, b2) in enumerate(zip(c1, c2)):
        xor = b1 ^ b2
        for bit in range(8):
            if xor & (1 << bit):
                diff_bits.append(i * 8 + bit)
                bits_flipped += 1

    percentage = (bits_flipped / total_bits * 100) if total_bits else 0.0

    return {
        "original_ciphertext": c1,
        "modified_ciphertext": c2,
        "diff_bits": diff_bits,
        "bits_flipped": bits_flipped,
        "total_bits": total_bits,
        "percentage": percentage,
        "key": key,
        "iv": iv,
        "byte_index": byte_index,
        "bit_mask": bit_mask,
    }
