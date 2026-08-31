# MedVault — Secure Hospital Document Exchange System

MedVault is a cryptographic framework designed for secure hospital electronic medical record (EMR) exchange, demonstrating symmetric encryption primitives, hybrid key wrapping, key agreement, and active vulnerability analysis.

---

## 🏥 Project Overview

### Task A — Symmetric Encryption & Analysis
- **`aes_encrypt.py`**:
  - Implements **AES-128 in CBC mode** with PKCS7 padding.
  - Automatically generates and exports 16-byte key (`key.bin`) and initialization vector (`iv.bin`).
  - Encrypts `patient_report.txt` $\rightarrow$ `patient_report_AES_encrypted.bin` and decrypts back with byte-level verification.
  - Benchmarks execution time across 1 KB, 100 KB, and 1 MB datasets.

- **`des_encrypt.py`**:
  - Implements **3-DES (Triple DES) in CBC mode** with 24-byte key and 8-byte block/IV padding.
  - Encrypts `patient_report.txt` $\rightarrow$ `patient_report_3DES_encrypted.bin` and decrypts back to verified plaintext.
  - Measures execution time across 1 KB, 100 KB, and 1 MB datasets.

- **`avalanche.py`**:
  - Quantifies the **Avalanche Effect** in AES-128 CBC.
  - Flips a single bit in byte 0 (`modified[0] ^= 0x01`) and compares ciphertexts bit-by-bit using XOR difference counting ($\approx 49.95\%$ bit alteration).

- **`ecb_vs_cbc_image.py`**:
  - Uses bitmap headers (54-byte BMP header preservation) to visually compare ECB vs. CBC mode behavior on raw pixel matrices.
  - `sample.bmp`: Original test image containing geometric visual data.
  - `ecb_output.bmp`: Demonstrates pattern leakage (identical plaintext blocks yield identical ciphertext blocks).
  - `cbc_output.bmp`: Demonstrates pseudo-random diffusion (CBC block chaining destroys visual structure).

---

### Task B — Asymmetric Key Exchange & Hybrid Encryption (`task_b/`)
- **`task_b/rsa_keygen.py`**:
  - Generates 2048-bit RSA key pair for the Receiver:
    - `receiver_private.pem`: Receiver's private decryption key (kept confidential).
    - `receiver_public.pem`: Receiver's public encryption key (distributed to Sender).

- **`task_b/hybrid_encrypt.py`**:
  - Implements **RSA-OAEP + AES-128 CBC Hybrid Envelope Encryption**.
  - **Sender**: Encrypts the 128-bit AES session key (`key.bin`) with Receiver's RSA public key $\rightarrow$ `encrypted_aes_key.bin`.
  - **Receiver**: Decrypts the RSA envelope using `receiver_private.pem` to recover the AES key, then decrypts the medical record $\rightarrow$ `patient_report_hybrid_decrypted.txt`.

- **`task_b/diffie_hellman.py`**:
  - Implements **Diffie-Hellman Key Agreement** over cyclic groups ($g=2$, $p$ prime modulus).
  - Demonstrates mutual derivation of a shared secret without ever transmitting the secret over the wire.

- **`task_b/mitm_attack.py`**:
  - Simulates active **Man-in-the-Middle (MITM)** interception by an adversary ("Mallory") on unauthenticated Diffie-Hellman.
  - Demonstrates how Mallory establishes separate shared secrets with both endpoints and explains cryptographic countermeasures (digital signatures, PKI, and TLS certificates).

---

## 📊 Performance Benchmarks (AES-128 vs. 3-DES)

| File Size | AES-128 CBC Encryption Time | 3-DES CBC Encryption Time | Speedup Factor |
| :--- | :--- | :--- | :--- |
| **~1 KB** (`test_1kb.txt`) | **0.23 ms** | 1.47 ms | **~6.3x faster** |
| **~100 KB** (`test_100kb.txt`) | **1.01 ms** | 19.53 ms | **~19.3x faster** |
| **~1 MB** (`test_1mb.txt`) | **9.56 ms** | 130.88 ms | **~13.7x faster** |

---

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate
pip install pycryptodome Pillow cryptography
```

### 2. Run Task A
```bash
python aes_encrypt.py
python des_encrypt.py
python avalanche.py
python ecb_vs_cbc_image.py
```

### 3. Run Task B
```bash
cd task_b
python rsa_keygen.py
python hybrid_encrypt.py
python diffie_hellman.py
python mitm_attack.py
```
