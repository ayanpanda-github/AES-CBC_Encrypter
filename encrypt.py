#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend

def encrypt_file(password, filename):
    if not Path(filename).exists():
        print(f"❌ File not found: {filename}")
        return False
    
    with open(filename, "rb") as f:
        data = f.read()
    
    salt = os.urandom(16)
    iv = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    key = kdf.derive(password.encode("utf-8"))
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    output_file = filename + ".enc"
    with open(output_file, "wb") as f:
        f.write(salt + iv + encrypted_data)
    
    print(f"✅ Encrypted: {filename} -> {output_file}")
    return True

def decrypt_file(password, filename):
    if not Path(filename).exists():
        print(f"❌ File not found: {filename}")
        return False
    
    with open(filename, "rb") as f:
        encrypted_file = f.read()
    
    salt = encrypted_file[:16]
    iv = encrypted_file[16:32]
    encrypted_data = encrypted_file[32:]
    
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    key = kdf.derive(password.encode("utf-8"))
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    output_file = filename.replace(".enc", "_decrypted")
    with open(output_file, "wb") as f:
        f.write(data)
    
    print(f"✅ Decrypted: {filename} -> {output_file}")
    return True

def main():
    print("🔐 AES-256 File Encryptor")
    print("=" * 30)
    
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python encrypt.py encrypt password filename")
        print("  python encrypt.py decrypt password filename.enc")
        print()
        print("Examples:")
        print("  python encrypt.py encrypt mypass123 document.txt")
        print("  python encrypt.py decrypt mypass123 document.txt.enc")
        return
    
    operation = sys.argv[1].lower()
    password = sys.argv[2]
    filename = sys.argv[3]
    
    if operation == "encrypt":
        encrypt_file(password, filename)
    elif operation == "decrypt":
        decrypt_file(password, filename)
    else:
        print("❌ Invalid operation. Use 'encrypt' or 'decrypt'")

if __name__ == "__main__":
    main()
