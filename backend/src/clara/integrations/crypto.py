import base64
import hashlib

from cryptography.fernet import Fernet

from clara.config import get_settings


def _get_fernet() -> Fernet:
    """Derive a Fernet key from the app's secret_key."""
    secret = get_settings().secret_key.get_secret_value().encode()
    # Fernet requires a 32-byte url-safe base64 key; derive via SHA-256
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a credential string, return base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_credential(ciphertext: str) -> str:
    """Decrypt a base64-encoded ciphertext back to plaintext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
