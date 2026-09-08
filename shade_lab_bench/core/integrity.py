"""
SHA-256 integrity verification and ciphertext tampering simulation.
Shared by the Integrity cards and reused internally by the (future) digital
signature card -- see claude.md: hashing logic must live in exactly one place.
"""

import hashlib


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_integrity(data: bytes, expected_hash: str) -> dict:
    actual_hash = compute_sha256(data)
    return {
        "actual_hash": actual_hash,
        "expected_hash": expected_hash,
        "match": actual_hash == expected_hash,
    }


def tamper_bytes(ciphertext: bytes, positions_and_masks: list) -> dict:
    """
    positions_and_masks: list of (index, xor_mask) tuples, e.g. [(10, 0xFF), (50, 0xAA)]
    Returns: {"tampered": bytes, "applied": list[(index, mask)]}
    Positions beyond the ciphertext length are skipped (and reported) rather
    than raising, so the UI can offer a slider without needing to clamp first.
    """
    tampered = bytearray(ciphertext)
    applied = []
    for index, mask in positions_and_masks:
        if 0 <= index < len(tampered):
            tampered[index] ^= mask
            applied.append((index, mask))
    return {"tampered": bytes(tampered), "applied": applied}
