"""RSA key generation and RSA-OAEP envelope operations for the lab cards."""

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad


def generate_rsa_keypair(bits: int = 2048) -> dict:
    """Generate a receiver RSA key pair without exporting it to disk."""
    key = RSA.generate(bits)
    return {
        "private_key": key.export_key(),
        "public_key": key.publickey().export_key(),
        "bits": key.size_in_bits(),
    }


def hybrid_encrypt_decrypt(
    plaintext: bytes, aes_key: bytes, iv: bytes, ciphertext: bytes,
    public_key: bytes, private_key: bytes,
) -> dict:
    """Wrap an AES session key with RSA-OAEP, unwrap it, then recover the payload."""
    pub_key = RSA.import_key(public_key)
    priv_key = RSA.import_key(private_key)
    encrypted_aes_key = PKCS1_OAEP.new(pub_key).encrypt(aes_key)
    recovered_aes_key = PKCS1_OAEP.new(priv_key).decrypt(encrypted_aes_key)
    recovered_plaintext = unpad(
        AES.new(recovered_aes_key, AES.MODE_CBC, iv).decrypt(ciphertext), 16
    )
    return {
        "encrypted_aes_key": encrypted_aes_key,
        "recovered_aes_key": recovered_aes_key,
        "recovered_plaintext": recovered_plaintext,
        "match": recovered_plaintext == plaintext,
    }
