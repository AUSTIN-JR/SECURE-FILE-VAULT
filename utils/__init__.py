import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

SALT_SIZE = 16
IV_SIZE = 16
HASH_SIZE = 64
HEADER_SIZE = SALT_SIZE + IV_SIZE + HASH_SIZE
PBKDF2_ITERATIONS = 100_000

def encrypt_bytes(raw_data: bytes, password: str) -> bytes:
    salt = get_random_bytes(SALT_SIZE)
    iv = get_random_bytes(IV_SIZE)

    key = PBKDF2(
        password,
        salt,
        dkLen=32,
        count=PBKDF2_ITERATIONS,
        hmac_hash_module=hashlib.sha256
    )

    original_hash = hashlib.sha256(raw_data).hexdigest().encode('ascii')

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(raw_data, AES.block_size))

    return salt + iv + original_hash + ciphertext

def decrypt_bytes(encrypted_data: bytes, password: str) -> tuple[bytes, str]:
    if len(encrypted_data) < HEADER_SIZE + AES.block_size:
        raise ValueError("Invalid payload: File is too short or corrupted.")

    salt = encrypted_data[:SALT_SIZE]
    iv = encrypted_data[SALT_SIZE:SALT_SIZE + IV_SIZE]
    stored_hash = encrypted_data[SALT_SIZE + IV_SIZE:HEADER_SIZE].decode('ascii', errors='ignore')
    ciphertext = encrypted_data[HEADER_SIZE:]

    key = PBKDF2(
        password,
        salt,
        dkLen=32,
        count=PBKDF2_ITERATIONS,
        hmac_hash_module=hashlib.sha256
    )
    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        decrypted_padded = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted_padded, AES.block_size)
    except (ValueError, KeyError):
        raise ValueError("Invalid password or corrupted ciphertext.")

    calculated_hash = hashlib.sha256(plaintext).hexdigest()
    if calculated_hash != stored_hash:
        raise ValueError("Integrity check failed: File has been tampered with.")

    return plaintext, calculated_hash