"""
ECB vs CBC visual pattern-leakage demonstration: encrypts the raw pixel bytes
of a BMP under both modes and reassembles a valid BMP for each, so ECB's
block-repetition weakness is visible directly in the output image.
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

from core.sample_data import BMP_HEADER_SIZE


def encrypt_bmp_pixels(bmp_bytes: bytes, key: bytes = None, mode: str = "CBC") -> dict:
    """
    Splits a BMP into header (first BMP_HEADER_SIZE bytes, kept intact so the
    file stays a valid, viewable image) and pixel data (encrypted).

    mode: "ECB" or "CBC"
    Returns: {"output_bmp": bytes, "key": bytes, "iv": bytes|None, "mode": str}
    """
    key = key or get_random_bytes(16)
    header = bmp_bytes[:BMP_HEADER_SIZE]
    pixels = bmp_bytes[BMP_HEADER_SIZE:]
    padded = pad(pixels, AES.block_size)

    if mode == "ECB":
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted = cipher.encrypt(padded)
        iv = None
    else:
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded)

    # Truncate back to original pixel length so the BMP dimensions stay valid
    # for display purposes (this is a demonstration, not a reversible export).
    output_pixels = encrypted[: len(pixels)]
    output_bmp = header + output_pixels

    return {"output_bmp": output_bmp, "key": key, "iv": iv, "mode": mode}
