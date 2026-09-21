# AES-256 Vault: Secure File Encryption Engine

A full-stack cryptography application implementing password-derived authenticated symmetric encryption and tamper verification.

## Features
- **AES-256-CBC:** Strong symmetric block encryption with standard PKCS#7 padding.
- **PBKDF2 Key Derivation:** 100,000 iterations using HMAC-SHA256 and 16-byte random salts.
- **Payload Integrity:** Built-in SHA-256 validation prevents altered or damaged files from decrypting.
- **In-Memory Streaming:** Server handles payload bytes directly in memory to avoid residual unencrypted data on disk.
- **Dual Interface:** Web dashboard (Flask + Fetch/XHR Progress) and CLI utility.

## Setup & Execution
1. Create environment: `python -m venv venv && venv\Scripts\activate`
2. Install packages: `pip install -r requirements.txt`
3. Launch web app: `python app.py`
4. Run CLI: `python cli.py --help`