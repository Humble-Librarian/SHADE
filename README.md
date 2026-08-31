# MedVault — Secure Hospital Document Exchange System

MedVault is a cryptographic framework designed for secure hospital electronic medical record (EMR) exchange, demonstrating symmetric encryption primitives, diffusion analysis, and cipher mode security characteristics.

---

## 🏥 Project Overview & Task A Implementation

### 1. Symmetric Encryption Suites
- **`aes_encrypt.py`**:
  - Implements **AES-128 in CBC mode** with PKCS7 padding.
  - Automatically generates and exports 16-byte key (`key.bin`) and initialization vector (`iv.bin`) for downstream asymmetric key wrapping.
  - Encrypts `patient_report.txt` $\rightarrow$ `patient_report_AES_encrypted.bin` and decrypts back with byte-level verification.
  - Benchmarks execution time across 1 KB, 100 KB, and 1 MB datasets.

- **`des_encrypt.py`**:
  - Implements **3-DES (Triple DES) in CBC mode** with 24-byte key and 8-byte block/IV padding.
  - Encrypts `patient_report.txt` $\rightarrow$ `patient_report_3DES_encrypted.bin` and decrypts back to verified plaintext.
  - Measures execution time across 1 KB, 100 KB, and 1 MB datasets.

### 2. Cryptographic Diffusion Analysis
- **`avalanche.py`**:
  - Quantifies the **Avalanche Effect** in AES-128 CBC.
  - Flips a single bit in byte 0 (`modified[0] ^= 0x01`) and compares ciphertexts bit-by-bit using XOR difference counting.
  - Achieves optimal diffusion ($\approx 49.95\%$ bit alteration).

### 3. Block Cipher Mode Analysis (ECB vs. CBC)
- **`ecb_vs_cbc_image.py`**:
  - Uses bitmap headers (54-byte BMP header preservation) to visually compare ECB vs. CBC mode behavior on raw pixel matrices.
  - `sample.bmp`: Original test image containing geometric visual data.
  - `ecb_output.bmp`: Demonstrates pattern leakage (identical plaintext blocks yield identical ciphertext blocks).
  - `cbc_output.bmp`: Demonstrates pseudo-random diffusion (CBC block chaining destroys visual structure).

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
pip install pycryptodome Pillow
```

### 2. Run Scripts
```bash
# 1. AES Encryption & Benchmark
python aes_encrypt.py

# 2. 3-DES Encryption & Benchmark
python des_encrypt.py

# 3. Avalanche Effect Analysis
python avalanche.py

# 4. ECB vs CBC Visual Analysis
python ecb_vs_cbc_image.py
```
