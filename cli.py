import argparse
import sys
from utils.encryption import encrypt_bytes, decrypt_bytes

def main():
    parser = argparse.ArgumentParser(description="AES-256 File Encryption/Decryption CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encrypt parser
    enc_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    enc_parser.add_argument("file", help="Path to the file to encrypt")
    enc_parser.add_argument("--password", required=True, help="Passphrase for key derivation")

    # Decrypt parser
    dec_parser = subparsers.add_parser("decrypt", help="Decrypt an encrypted .enc file")
    dec_parser.add_argument("file", help="Path to the .enc file")
    dec_parser.add_argument("--password", required=True, help="Passphrase used during encryption")

    args = parser.parse_args()

    try:
        if args.command == "encrypt":
            with open(args.file, "rb") as f:
                data = f.read()
            encrypted = encrypt_bytes(data, args.password)
            out_file = args.file + ".enc"
            with open(out_file, "wb") as f:
                f.write(encrypted)
            print(f"[+] Encrypted successfully -> {out_file}")

        elif args.command == "decrypt":
            with open(args.file, "rb") as f:
                encrypted_data = f.read()
            decrypted, verified_hash = decrypt_bytes(encrypted_data, args.password)
            
            out_file = args.file[:-4] if args.file.endswith(".enc") else "decrypted_" + args.file
            with open(out_file, "wb") as f:
                f.write(decrypted)
            print(f"[+] Decrypted successfully -> {out_file}")
            print(f"[+] Integrity Verified (SHA-256): {verified_hash}")

    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()