#!/usr/bin/env python3
import os
import sys
import getpass
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        print("⚠️  Warning: Password is less than 8 characters. Consider using a stronger password.")
    return True

def encrypt_file(password, filename):
    """Encrypt a file using AES-256 in CBC mode"""
    try:
        # Validate inputs
        if not password:
            print("❌ Error: Password cannot be empty")
            return False
        
        validate_password(password)
        
        file_path = Path(filename)
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            return False
        
        if not file_path.is_file():
            print(f"❌ Path is not a file: {filename}")
            return False
        
        # Check if output file already exists
        output_file = str(file_path) + ".enc"
        if Path(output_file).exists():
            response = input(f"Output file {output_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return False
        
        print(f"📖 Reading file: {filename}")
        with open(filename, "rb") as f:
            data = f.read()
        
        if len(data) == 0:
            print("⚠️  Warning: File is empty")
        
        print("🔐 Encrypting data...")
        # Generate random salt and IV
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), 
            length=32, 
            salt=salt, 
            iterations=100000, 
            backend=default_backend()
        )
        key = kdf.derive(password.encode("utf-8"))
        
        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        print(f"💾 Writing encrypted file: {output_file}")
        with open(output_file, "wb") as f:
            f.write(salt + iv + encrypted_data)
        
        print(f"✅ Successfully encrypted: {filename} -> {output_file}")
        return True
        
    except PermissionError:
        print(f"❌ Permission denied: Cannot read {filename} or write to output directory")
        return False
    except OSError as e:
        print(f"❌ File system error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during encryption: {e}")
        return False

def decrypt_file(password, filename):
    """Decrypt a file that was encrypted with AES-256 in CBC mode"""
    try:
        # Validate inputs
        if not password:
            print("❌ Error: Password cannot be empty")
            return False
        
        file_path = Path(filename)
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            return False
        
        if not file_path.is_file():
            print(f"❌ Path is not a file: {filename}")
            return False
        
        print(f"📖 Reading encrypted file: {filename}")
        with open(filename, "rb") as f:
            encrypted_file = f.read()
        
        # Validate file format
        if len(encrypted_file) < 32:  # At least salt (16) + IV (16) bytes
            print("❌ Invalid encrypted file format: File too small")
            return False
        
        # Extract components
        salt = encrypted_file[:16]
        iv = encrypted_file[16:32]
        encrypted_data = encrypted_file[32:]
        
        if len(encrypted_data) == 0:
            print("❌ Invalid encrypted file format: No encrypted data found")
            return False
        
        # Determine output filename
        if filename.endswith(".enc"):
            # Remove .enc extension and get original filename
            base_name = filename[:-4]
            output_file = base_name + "_decrypted" + Path(base_name).suffix
            # If original had no extension, don't add extra dot
            if not Path(base_name).suffix:
                output_file = base_name + "_decrypted"
        else:
            output_file = filename + "_decrypted"
        
        # Check if output file already exists
        if Path(output_file).exists():
            response = input(f"Output file {output_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return False
        
        print("🔓 Deriving key from password...")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), 
            length=32, 
            salt=salt, 
            iterations=100000, 
            backend=default_backend()
        )
        key = kdf.derive(password.encode("utf-8"))
        
        print("🔐 Decrypting data...")
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        print(f"💾 Writing decrypted file: {output_file}")
        with open(output_file, "wb") as f:
            f.write(data)
        
        print(f"✅ Successfully decrypted: {filename} -> {output_file}")
        return True
        
    except PermissionError:
        print(f"❌ Permission denied: Cannot read {filename} or write to output directory")
        return False
    except ValueError as e:
        if "Invalid padding" in str(e) or "padding bytes" in str(e):
            print("❌ Decryption failed: Invalid password or corrupted file")
        else:
            print(f"❌ Invalid data format: {e}")
        return False
    except OSError as e:
        print(f"❌ File system error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during decryption: {e}")
        return False

def interactive_mode():
    """Run the program in interactive mode with secure password input"""
    print("\n📋 Choose an operation:")
    print("1. Encrypt a file")
    print("2. Decrypt a file")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "3":
                print("👋 Goodbye!")
                return
            elif choice in ["1", "2"]:
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return
    
    # Get filename
    while True:
        try:
            filename = input("Enter the filename (with path if not in current directory): ").strip()
            if filename:
                break
            else:
                print("❌ Please enter a valid filename.")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Operation cancelled.")
            return
    
    # Get password securely
    while True:
        try:
            if choice == "1":
                password = getpass.getpass("Enter password for encryption: ")
                if password:
                    confirm_password = getpass.getpass("Confirm password: ")
                    if password == confirm_password:
                        break
                    else:
                        print("❌ Passwords don't match. Please try again.")
                else:
                    print("❌ Password cannot be empty.")
            else:
                password = getpass.getpass("Enter password for decryption: ")
                if password:
                    break
                else:
                    print("❌ Password cannot be empty.")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Operation cancelled.")
            return
    
    # Perform the operation
    if choice == "1":
        encrypt_file(password, filename)
    else:
        decrypt_file(password, filename)

def main():
    print("🔐 AES-256 File Encryptor")
    print("=" * 30)
    
    # Check if running in command-line mode or interactive mode
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_mode()
    elif len(sys.argv) == 4:
        # Command-line mode
        operation = sys.argv[1].lower()
        password = sys.argv[2]
        filename = sys.argv[3]
        
        print("⚠️  Warning: Password visible in command line. Consider using interactive mode.")
        
        if operation == "encrypt":
            encrypt_file(password, filename)
        elif operation == "decrypt":
            decrypt_file(password, filename)
        else:
            print("❌ Invalid operation. Use 'encrypt' or 'decrypt'")
    else:
        # Show usage
        print("Usage:")
        print("  python encrypt.py                              # Interactive mode (recommended)")
        print("  python encrypt.py encrypt password filename    # Command line mode")
        print("  python encrypt.py decrypt password filename.enc # Command line mode")
        print()
        print("Examples:")
        print("  python encrypt.py                              # Start interactive mode")
        print("  python encrypt.py encrypt mypass123 document.txt")
        print("  python encrypt.py decrypt mypass123 document.txt.enc")
        print()
        print("💡 Tip: Use interactive mode to avoid exposing passwords in command history.")

if __name__ == "__main__":
    main()
