<div align="center">

# 🏥 MedVault — Cryptographic Hospital Document Exchange System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Cryptography](https://img.shields.io/badge/Cryptography-pycryptodome%20%7C%20cryptography-darkgreen.svg)](https://pycryptodome.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-AES--128%20%7C%20RSA--2048%20%7C%20SHA--256-orange.svg)](#)

*An end-to-end cryptographic suite demonstrating symmetric encryption primitives, hybrid envelope encryption, Diffie-Hellman key agreement, active MITM interception, and SHA-256 data integrity verification for Electronic Medical Records (EMR).*

---

</div>

## 📌 Table of Contents
- [System Architecture](#-system-architecture)
- [Task A: Symmetric Encryption & Mode Analysis](#-task-a-symmetric-encryption--mode-analysis)
  - [AES-128 vs. 3-DES Benchmarks](#1-performance-benchmarks-aes-128-vs-3-des)
  - [Avalanche Effect Analysis](#2-avalanche-effect-analysis)
  - [ECB vs. CBC Visual Pattern Leakage](#3-ecb-vs-cbc-mode-visual-analysis)
- [Task B: Asymmetric Key Exchange & Hybrid Encryption](#-task-b-asymmetric-key-exchange--hybrid-encryption)
  - [B1: RSA-2048 Key Generation & Hybrid Encryption](#b1-rsa-2048-key-generation--hybrid-envelope-encryption)
  - [B2: Diffie-Hellman Key Agreement](#b2-diffie-hellman-key-exchange)
  - [B3: Man-In-The-Middle (MITM) Simulation](#b3-man-in-the-middle-mitm-attack-simulation)
- [Task C: Cryptographic Integrity & Tamper Detection](#-task-c-cryptographic-integrity--tamper-detection)
  - [C1: SHA-256 Checksum Verification](#c1-sha-256-document-integrity-verification)
  - [C2: Active Ciphertext Tampering Detection](#c2-active-ciphertext-tampering-simulation)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Quick Start](#-installation--quick-start)

---

## 🏗 System Architecture

```
+---------------------------------------------------------------------------------------+
|                                    SENDER (Doctor / Clinic)                           |
+---------------------------------------------------------------------------------------+
|  1. Plaintext EMR (patient_report.txt)                                                |
|  2. AES-128-CBC Encrypt:  Ciphertext = AES_CBC(Plaintext, Key_AES, IV)                |
|  3. RSA-OAEP Wrap:        Encrypted_Key = RSA_OAEP_Encrypt(Key_AES, PubKey_Receiver)   |
|  4. Integrity Digest:     Hash_Original = SHA256(Plaintext)                           |
+-------------------------------------------+-------------------------------------------+
                                            |
                         TRANSMISSION ENVELOPE (In-Transit)
                         - patient_report_AES_encrypted.bin
                         - encrypted_aes_key.bin
                         - iv.bin
                         - original_hash.txt
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                  RECEIVER (Hospital / Specialist)                     |
+---------------------------------------------------------------------------------------+
|  1. RSA-OAEP Unwrap:      Key_AES = RSA_OAEP_Decrypt(Encrypted_Key, PrivKey_Receiver) |
|  2. AES-128-CBC Decrypt:  Plaintext = AES_CBC_Decrypt(Ciphertext, Key_AES, IV)       |
|  3. Integrity Check:      Hash_Received = SHA256(Plaintext)                           |
|                           VERIFY: (Hash_Original == Hash_Received)                    |
+---------------------------------------------------------------------------------------+
```

---

## 🔐 Task A: Symmetric Encryption & Mode Analysis

### 1. Performance Benchmarks: AES-128 vs. 3-DES
Both ciphers were evaluated in CBC mode across three distinct payload sizes ($1\text{ KB}$, $100\text{ KB}$, and $1\text{ MB}$):

| File Sizing | Dataset File | AES-128 CBC Time | 3-DES CBC Time | Speedup Factor (AES) |
| :--- | :--- | :--- | :--- | :--- |
| **~1 KB** | `test_1kb.txt` | **0.2344 ms** | 1.4720 ms | **~6.3x faster** |
| **~100 KB** | `test_100kb.txt` | **1.0140 ms** | 19.5327 ms | **~19.3x faster** |
| **~1 MB** | `test_1mb.txt` | **9.5637 ms** | 130.8837 ms | **~13.7x faster** |

> **Key Takeaway**: AES is significantly faster than 3-DES due to modern byte substitution-permutation networks and hardware-level optimization (AES-NI), while 3-DES requires 3 sequential DES operations with 64-bit block bottlenecks.

---

### 2. Avalanche Effect Analysis
The avalanche effect measures cryptographic diffusion: flipping a single bit in the plaintext should alter approximately $50\%$ of ciphertext bits.

- **Original Plaintext byte 0**: `0b00111101`
- **Modified Plaintext byte 0**: `0b00111100` (1 bit flipped via `^= 0x01`)
- **Total Bits Tested**: $30,080\text{ bits}$
- **Bits Inverted in Ciphertext**: $15,026\text{ bits}$
- **Measured Avalanche Effect**: **`49.95%`** (Optimal target: $45\% - 55\%$)

```bash
python avalanche.py
```

---

### 3. ECB vs. CBC Mode Visual Analysis
Bitmap header extraction ($54\text{ bytes}$) was used to isolate and encrypt raw RGB pixel data, highlighting the vulnerability of Electronic Codebook (ECB) mode:

| Mode | Visual Representation | Observation |
| :--- | :--- | :--- |
| **Original** (`sample.bmp`) | Clear blue geometric graphic | Unencrypted source image |
| **ECB Mode** (`ecb_output.bmp`) | High pattern leakage | Identical plaintext blocks encrypt into identical ciphertext blocks; shapes remain clearly visible |
| **CBC Mode** (`cbc_output.bmp`) | Pure pseudo-random noise | Ciphertext block chaining XORs previous blocks, completely eliminating visual patterns |

---

## 🔑 Task B: Asymmetric Key Exchange & Hybrid Encryption

All scripts for Task B reside in [`task_b/`](task_b/).

### B1: RSA-2048 Key Generation & Hybrid Envelope Encryption
1. **`task_b/rsa_keygen.py`**:
   - Generates a **2048-bit RSA key pair**:
     - `receiver_private.pem` ($1,674\text{ bytes}$): Confidential private key used by receiver for decryption.
     - `receiver_public.pem` ($450\text{ bytes}$): Public key shared with senders.
2. **`task_b/hybrid_encrypt.py`**:
   - **Sender**: Uses `PKCS1_OAEP` to encrypt the 128-bit AES session key (`key.bin`) using `receiver_public.pem` $\rightarrow$ `encrypted_aes_key.bin` ($256\text{ bytes}$).
   - **Receiver**: Decrypts `encrypted_aes_key.bin` using `receiver_private.pem`, recovering the session key to decrypt `patient_report_AES_encrypted.bin`.
   - Verified bit-for-bit equality with original medical record.

---

### B2: Diffie-Hellman Key Exchange
**`task_b/diffie_hellman.py`**:
- Simulates independent derivation of a mutual shared secret over cyclic group parameters ($g=2$, $p$ prime modulus):
  $$\text{Sender}: A = g^a \pmod p \quad \longrightarrow \quad \text{Receiver}: B = g^b \pmod p$$
  $$\text{Shared Secret} = B^a \pmod p = A^b \pmod p$$
- Both parties compute the identical 64-byte shared secret without ever transmitting confidential key material over the network.

---

### B3: Man-In-The-Middle (MITM) Attack Simulation
**`task_b/mitm_attack.py`**:
- Simulates an active adversary ("Mallory") intercepting public values $A$ and $B$, substituting them with Mallory's public key $M$.
- **Result**: Mallory establishes two distinct shared secrets:
  - $\text{Secret}_{\text{Mallory}\leftrightarrow\text{Sender}}$
  - $\text{Secret}_{\text{Mallory}\leftrightarrow\text{Receiver}}$
- Demonstrates that raw Diffie-Hellman lacks authentication.
- **Countermeasures**:
  1. **Station-to-Station (STS) Protocol**: Digitally sign public keys.
  2. **Public Key Infrastructure (PKI)**: X.509 Certificate Authorities validating identities (TLS/HTTPS).

---

## 🛡️ Task C: Cryptographic Integrity & Tamper Detection

All scripts for Task C reside in [`task_c/`](task_c/).

### C1: SHA-256 Document Integrity Verification
**`task_c/integrity_check.py`**:
- Sender computes cryptographic digest before transmission:
  ```
  SHA-256 (original): 07d3927fef59fee630f946b0e3edac8c917c621289edfc3d86aead324a580d51
  ```
- Receiver decrypts payload, recomputes digest, and verifies match:
  ```
  ✅ Integrity Verified — hashes match perfectly!
  🔒 Proof: The document was NOT tampered with or corrupted during transmission.
  ```

---

### C2: Active Ciphertext Tampering Simulation
**`task_c/tamper_detection.py`**:
- Simulates an adversary flipping 2 bytes in transit:
  - Byte 10: `tampered[10] ^= 0xFF`
  - Byte 50: `tampered[50] ^= 0xAA`
- Receiver decrypts the damaged stream and computes SHA-256:
  ```
  Expected SHA-256 (Original) : 07d3927fef59fee630f946b0e3edac8c917c621289edfc3d86aead324a580d51
  Calculated SHA-256 (Tampered): 7eb95cb0aeb9564e4cc552212d06629b3033ee7353cf3784dd6802186b204f00

  🚨 ALERT: Hash mismatch — tampering detected!
  ❌ Document integrity check failed! The corrupted file was immediately rejected.
  ```

---

## 📂 Project Directory Structure

```
Hospital-Document-Exchange/
├── .gitignore
├── README.md
│
├── [ Task A — Symmetric Ciphers & Mode Analysis ]
├── aes_encrypt.py                     # AES-128 CBC encryption, verification & benchmarks
├── des_encrypt.py                     # 3-DES CBC encryption, verification & benchmarks
├── avalanche.py                       # 1-bit flip bitwise XOR avalanche effect calculation
├── ecb_vs_cbc_image.py                # Visual demonstration of ECB vs CBC on BMP bitmaps
├── key.bin                            # Generated 16-byte AES session key
├── iv.bin                             # Generated 16-byte AES initialization vector
├── patient_report.txt                 # Original hospital electronic medical record
├── patient_report_AES_encrypted.bin   # AES ciphertext
├── patient_report_AES_decrypted.txt   # AES verified decrypted plaintext
├── patient_report_3DES_encrypted.bin  # 3-DES ciphertext
├── patient_report_3DES_decrypted.txt  # 3-DES verified decrypted plaintext
├── sample.bmp                         # Original BMP test image
├── ecb_output.bmp                     # ECB encrypted BMP (shows pattern leakage)
├── cbc_output.bmp                     # CBC encrypted BMP (pseudo-random noise)
├── test_1kb.txt                       # 1 KB benchmark dataset
├── test_100kb.txt                     # 100 KB benchmark dataset
├── test_1mb.txt                       # 1 MB benchmark dataset
│
├── task_b/                            # [ Task B — Asymmetric & Key Agreement ]
│   ├── rsa_keygen.py                  # Generates 2048-bit RSA key pair
│   ├── hybrid_encrypt.py              # RSA-OAEP session key wrapping & EMR recovery
│   ├── diffie_hellman.py              # Diffie-Hellman shared secret agreement
│   ├── mitm_attack.py                 # Active MITM interception simulation & PKI mitigations
│   ├── receiver_private.pem           # Receiver's RSA private key (Confidential)
│   ├── receiver_public.pem            # Receiver's RSA public key (Shared)
│   ├── encrypted_aes_key.bin          # RSA-OAEP encrypted AES key (256 bytes)
│   └── patient_report_hybrid_decrypted.txt
│
└── task_c/                            # [ Task C — Integrity & Tamper Detection ]
    ├── integrity_check.py             # SHA-256 checksum generation & validation
    ├── tamper_detection.py            # Ciphertext corruption & active detection alert
    ├── original_hash.txt              # SHA-256 digest string of original EMR
    ├── patient_report_TAMPERED.bin    # Corrupted ciphertext
    ├── patient_report_TAMPERED_decrypted.txt
    └── patient_report_integrity_decrypted.txt
```

---

## ⚡ Installation & Quick Start

### 1. Prerequisites & Virtual Environment
```bash
git clone https://github.com/Humble-Librarian/MedVault.git
cd MedVault

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate          # On Windows PowerShell
# source venv/bin/activate       # On Linux / macOS

# Install required cryptographic packages
pip install pycryptodome Pillow cryptography
```

### 2. Running Task A (Symmetric Suite)
```bash
python aes_encrypt.py
python des_encrypt.py
python avalanche.py
python ecb_vs_cbc_image.py
```

### 3. Running Task B (Asymmetric Suite)
```bash
cd task_b
python rsa_keygen.py
python hybrid_encrypt.py
python diffie_hellman.py
python mitm_attack.py
cd ..
```

### 4. Running Task C (Integrity Suite)
```bash
cd task_c
python integrity_check.py
python tamper_detection.py
cd ..
```

---

<div align="center">
  <b>Developed for Secure Healthcare Cryptographic Exchanges</b><br>
  <sub>All patient data utilized in benchmarks is synthetic and generated strictly for cryptographic testing purposes.</sub>
</div>
