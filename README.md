<div align="center">

# 🏥 SHADE — Secure Hospital And Document Exchange

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Cryptography](https://img.shields.io/badge/Cryptography-pycryptodome%20%7C%20cryptography-darkgreen.svg)](https://pycryptodome.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-AES--128%20%7C%20RSA--2048%20%7C%20SHA--256%20%7C%20X.509%20%7C%20Kerberos-orange.svg)](#)

*An end-to-end cryptographic suite demonstrating symmetric encryption primitives, hybrid envelope encryption, Diffie-Hellman key agreement, active MITM interception, SHA-256 data integrity verification, RSA digital signatures, X.509 PKI certificates, and Kerberos ticket-granting authentication for Electronic Medical Records (EMR).*

---

</div>

## 📌 Table of Contents
- [Executive Overview](#-executive-overview)
- [System Architecture](#-system-architecture)
- [Interactive CLI Application (`shade_cli.py`)](#-interactive-cli-application-shade_clipy)
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
- [Task D: Digital Signatures, PKI & Access Control](#-task-d-digital-signatures-pki--access-control)
  - [D1: RSA Digital Signatures & Non-Repudiation](#d1-rsa-digital-signatures--tamper-testing)
  - [D2: X.509 Digital Certificates & Identity Binding](#d2-x509-digital-certificates--pki-simulation)
  - [D3: Kerberos Ticket-Granting Authentication](#d3-kerberos-authentication-protocol-simulation)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Quick Start](#-installation--quick-start)

---

## 🏥 Executive Overview

**SHADE (Secure Hospital And Document Exchange)** is an end-to-end cryptographic framework developed for hospital telemedicine networks and Electronic Medical Record (EMR) exchange. It models three fundamental actors:
1. **The Sender (Dr. Kavya Sharma / Clinic)**: Generates, encrypts, signs, and packages patient medical records.
2. **The Receiver (Dr. Rohan Desai / Hospital Specialist)**: Unwraps keys, decrypts payloads, verifies SHA-256 checksums, and authenticates digital signatures.
3. **The Adversary ("Mallory" / Network Interceptor)**: Simulates active MITM key injection and in-transit ciphertext corruption to validate security defenses.

---

## 🏗 System Architecture

```
+---------------------------------------------------------------------------------------+
|                                    SENDER (Dr. Kavya Sharma / Clinic)                 |
+---------------------------------------------------------------------------------------+
|  1. Plaintext EMR (patient_report.txt)                                                |
|  2. AES-128-CBC Encrypt:  Ciphertext = AES_CBC(Plaintext, Key_AES, IV)                |
|  3. RSA-OAEP Key Wrap:    Encrypted_Key = RSA_OAEP_Encrypt(Key_AES, PubKey_Receiver)   |
|  4. SHA-256 Integrity:    Hash_Original = SHA256(Plaintext)                           |
|  5. Digital Signature:    Signature = RSA_Sign(Hash_Original, PrivKey_Sender)         |
|  6. Identity Binding:     X.509 Certificate (Subject=Dr. Sender, PubKey_Sender)       |
+-------------------------------------------+-------------------------------------------+
                                            |
                         TRANSMISSION ENVELOPE (In-Transit)
                         - patient_report_AES_encrypted.bin
                         - encrypted_aes_key.bin
                         - iv.bin
                         - original_hash.txt
                         - document_signature.bin
                         - sender_certificate.pem
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                  RECEIVER (Dr. Rohan Desai / Hospital)                |
+---------------------------------------------------------------------------------------+
|  1. Certificate Validate: Verify X.509 Certificate & extract PubKey_Sender            |
|  2. RSA-OAEP Unwrap:      Key_AES = RSA_OAEP_Decrypt(Encrypted_Key, PrivKey_Receiver) |
|  3. AES-128-CBC Decrypt:  Plaintext = AES_CBC_Decrypt(Ciphertext, Key_AES, IV)       |
|  4. Integrity Verify:     Hash_Received = SHA256(Plaintext) == Hash_Original          |
|  5. Signature Verify:     RSA_Verify(Hash_Received, Signature, PubKey_Sender)        |
+---------------------------------------------------------------------------------------+
```

---

## 🖥 Interactive CLI Application (`shade_cli.py`)

In addition to automated batch testing, SHADE provides an interactive, stateful terminal console ([`shade_cli.py`](shade_cli.py)) allowing step-by-step exploration of each cryptographic primitive with live session status indicators (`[✅]`, `[⬜]`, `[❌]`) and strict dependency tracking.

```
╔══════════════════════════════════════════════════════╗
║     SHADE — Secure Hospital Document Exchange        ║
╠══════════════════════════════════════════════════════╣
║  Document : patient_report.txt   (9431 bytes)        ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  ── LAYER 1: SYMMETRIC ENCRYPTION ─────────────────  ║
║   1.  AES-128 CBC Encryption & Decryption    [⬜]    ║
║   2.  3-DES CBC Encryption & Decryption      [⬜]    ║
║   3.  Avalanche Effect Analysis              [⬜]    ║
║   4.  ECB vs CBC Image Comparison            [⬜]    ║
║                                                      ║
║  ── LAYER 2: ASYMMETRIC & KEY EXCHANGE ────────────  ║
║   5.  RSA-2048 Key Generation                [⬜]    ║
║   6.  Hybrid Envelope Encryption             [⬜]    ║
║   7.  Diffie-Hellman Key Exchange             [⬜]    ║
║   8.  MITM Attack Simulation                 [⬜]    ║
║                                                      ║
║  ── LAYER 3: INTEGRITY ────────────────────────────  ║
║   9.  SHA-256 Integrity Verification         [⬜]    ║
║  10.  Ciphertext Tamper Detection             [⬜]    ║
║                                                      ║
║  ── LAYER 4: AUTHENTICATION ───────────────────────  ║
║  11.  RSA Digital Signature (Sign)            [⬜]    ║
║  12.  Signature Verification                 [⬜]    ║
║  13.  X.509 Certificate Generation           [⬜]    ║
║  14.  Kerberos Authentication Simulation     [⬜]    ║
║                                                      ║
║  ── FULL PIPELINE ─────────────────────────────────  ║
║  15.  ▶ Run Complete SHADE Pipeline                  ║
║  16.  📋 Show Results Summary                        ║
║  17.  🔄 Reset All (start fresh)                     ║
║                                                      ║
║   0.  Exit                                           ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

### CLI Features:
- **Centralized `STATE` Dictionary**: Preserves in-memory keys, initialization vectors, ciphertexts, and certificates across steps without requiring redundant disk I/O.
- **Dependency Guard**: Warns and prevents out-of-order execution (e.g., attempting Hybrid Encryption before generating AES or RSA keys).
- **One-Click Execution**: Option 15 executes the full pipeline non-interactively and generates an instant session verification summary.

---

## 🔐 Task A: Symmetric Encryption & Mode Analysis

### 1. Performance Benchmarks: AES-128 vs. 3-DES
Both ciphers were evaluated in CBC mode across three distinct payload sizes ($1\text{ KB}$, $100\text{ KB}$, and $1\text{ MB}$):

| File Sizing | Dataset File | AES-128 CBC Time | 3-DES CBC Time | Speedup Factor (AES) |
| :--- | :--- | :--- | :--- | :--- |
| **~1 KB** | `test_1kb.txt` | **0.56 ms** | 1.61 ms | **~2.8x faster** |
| **~100 KB** | `test_100kb.txt` | **2.22 ms** | 19.04 ms | **~8.6x faster** |
| **~1 MB** | `test_1mb.txt` | **16.66 ms** | 227.92 ms | **~13.7x faster** |

> **Key Takeaway**: AES is significantly faster than 3-DES due to modern byte substitution-permutation networks and hardware-level optimization (AES-NI), while 3-DES requires 3 sequential DES operations with 64-bit block bottlenecks.

---

### 2. Avalanche Effect Analysis
The avalanche effect measures cryptographic diffusion: flipping a single bit in the plaintext should alter approximately $50\%$ of ciphertext bits.

- **Original Plaintext byte 0**: `0b00111101`
- **Modified Plaintext byte 0**: `0b00111100` (1 bit flipped via `^= 0x01`)
- **Total Bits Tested**: $75,520\text{ bits}$
- **Bits Inverted in Ciphertext**: $37,869\text{ bits}$
- **Measured Avalanche Effect**: **`50.14%`** (Optimal target: $45\% - 55\%$)

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
     - `receiver_private.pem` ($1,678\text{ bytes}$): Confidential private key used by receiver for decryption.
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
  SHA-256 (original): e5ae1671c36d24d5dd3f2b1111d0caaa4ff74d89493e63c5a7c897361859c680
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
  Expected SHA-256 (Original) : e5ae1671c36d24d5dd3f2b1111d0caaa4ff74d89493e63c5a7c897361859c680
  Calculated SHA-256 (Tampered): 7eb10bd712f0384c09577942c648d95404625e2894042236699e28585c64dc38

  🚨 ALERT: Hash mismatch — tampering detected!
  ❌ Document integrity check failed! The corrupted file was immediately rejected.
  ```

---

## 📜 Task D: Digital Signatures, PKI & Access Control

All scripts for Task D reside in [`task_d/`](task_d/).

### D1: RSA Digital Signatures & Tamper Testing
**`task_d/digital_signature.py`**:
- **Signing**: Sender hashes `patient_report.txt` with SHA-256 and signs the 32-byte hash using RSA PKCS#1 v1.5 with `sender_private.pem` $\rightarrow$ `document_signature.bin` ($256\text{ bytes}$).
- **Verification**: Receiver verifies signature using `sender_public.pem`.
- **Tamper Test**: Flipping a single bit in the medical report immediately causes the signature verification to fail (`❌ Signature Invalid`), proving **authenticity, integrity, and non-repudiation**.

---

### D2: X.509 Digital Certificates & PKI Simulation
**`task_d/x509_cert_sim.py`**:
- Binds Dr. Sender's identity (`CN=Dr. Sender, O=SHADE Hospital Network, ST=Gujarat, C=IN`) to their RSA-2048 public key.
- Self-signed using SHA-256 for a 365-day validity window $\rightarrow$ `sender_certificate.pem`.
- Receiver parses, extracts the public key, and validates certificate fields and expiration boundaries.

---

### D3: Kerberos Authentication Protocol Simulation
**`task_d/kerberos_sim.py`**:
- Simulates the 4-step Single Sign-On (SSO) ticket-granting exchange:
  1. **Client $\rightarrow$ AS**: Request authentication for `Dr. Sender`.
  2. **AS $\rightarrow$ Client**: Issue Ticket Granting Ticket (TGT) encrypted with TGS Master Key.
  3. **Client $\rightarrow$ TGS**: Present TGT and request Service Ticket for `HospitalRecordServer`.
  4. **TGS $\rightarrow$ Client**: Issue Service Ticket encrypted with Service Master Key.
  5. **Client $\rightarrow$ Server**: Present Service Ticket $\rightarrow$ Server decrypts ticket and grants access.

---

## 📂 Project Directory Structure

```
Hospital-Document-Exchange/
├── .gitignore
├── README.md
├── shade_cli.py                       # Interactive Stateful CLI Menu (17 Options)
├── demo.py                            # Master End-to-End SHADE Pipeline Runner (14 checks)
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
├── task_c/                            # [ Task C — Integrity & Tamper Detection ]
│   ├── integrity_check.py             # SHA-256 checksum generation & validation
│   ├── tamper_detection.py            # Ciphertext corruption & active detection alert
│   ├── original_hash.txt              # SHA-256 digest string of original EMR
│   ├── patient_report_TAMPERED.bin    # Corrupted ciphertext
│   ├── patient_report_TAMPERED_decrypted.txt
│   └── patient_report_integrity_decrypted.txt
│
└── task_d/                            # [ Task D — Digital Signatures, PKI & Access ]
    ├── digital_signature.py           # RSA PKCS#1 v1.5 signing, verification & tamper test
    ├── x509_cert_sim.py               # X.509 self-signed certificate generation & parsing
    ├── kerberos_sim.py                # 4-step Kerberos ticket granting simulation
    ├── sender_private.pem             # Sender's RSA private key for signing
    ├── sender_public.pem              # Sender's RSA public key for verification
    ├── document_signature.bin         # RSA digital signature on SHA-256 hash (256 bytes)
    └── sender_certificate.pem         # X.509 public key certificate
```

---

## ⚡ Installation & Quick Start

### 1. Prerequisites & Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Humble-Librarian/SHADE.git
cd SHADE

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate          # On Windows PowerShell
# source venv/bin/activate       # On Linux / macOS

# Install required cryptographic packages
pip install pycryptodome Pillow cryptography
```

### 2. Run Interactive CLI Menu
```bash
python shade_cli.py
```

### 3. Or Run Master Automated Pipeline
```bash
python demo.py
```

### 4. Or Run Tasks Individually

- **Task A (Symmetric Suite)**:
  ```bash
  python aes_encrypt.py
  python des_encrypt.py
  python avalanche.py
  python ecb_vs_cbc_image.py
  ```

- **Task B (Asymmetric Suite)**:
  ```bash
  cd task_b
  python rsa_keygen.py
  python hybrid_encrypt.py
  python diffie_hellman.py
  python mitm_attack.py
  cd ..
  ```

- **Task C (Integrity Suite)**:
  ```bash
  cd task_c
  python integrity_check.py
  python tamper_detection.py
  cd ..
  ```

- **Task D (Signatures, PKI & Access Control)**:
  ```bash
  cd task_d
  python digital_signature.py
  python x509_cert_sim.py
  python kerberos_sim.py
  cd ..
  ```

---

<div align="center">
  <b>SHADE — Secure Hospital And Document Exchange</b><br>
  <sub>All patient data utilized in benchmarks is synthetic and generated strictly for cryptographic testing purposes.</sub>
</div>
