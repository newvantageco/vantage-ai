"""
Database Encryption Utilities for VANTAGE AI
Provides secure encryption/decryption functions for sensitive data
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

class DatabaseEncryption:
    """Handles encryption and decryption of sensitive database data."""
    
    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryption with a key.
        
        Args:
            key: Encryption key. If None, will use environment variable or generate new key.
        """
        self.key = key or os.getenv('ENCRYPTION_KEY', self._generate_key())
        self.cipher = Fernet(self._derive_key(self.key))
    
    def _generate_key(self) -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()
    
    def _derive_key(self, password: str) -> bytes:
        """Derive a key from password using PBKDF2."""
        password_bytes = password.encode()
        salt = b'vantage_ai_salt_2024'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_pii(self, data: str) -> str:
        """
        Encrypt personally identifiable information.
        
        Args:
            data: PII data to encrypt
            
        Returns:
            Encrypted PII data
        """
        return self.encrypt(data)
    
    def decrypt_pii(self, encrypted_data: str) -> str:
        """
        Decrypt personally identifiable information.
        
        Args:
            encrypted_data: Encrypted PII data
            
        Returns:
            Decrypted PII data
        """
        return self.decrypt(encrypted_data)
    
    def create_hash_for_search(self, data: str) -> str:
        """
        Create a hash for searching without exposing original data.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash of the data
        """
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()

# Global encryption instance
_encryption_instance = None

def get_encryption() -> DatabaseEncryption:
    """Get the global encryption instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = DatabaseEncryption()
    return _encryption_instance

# Convenience functions
def encrypt_data(data: Union[str, bytes]) -> str:
    """Encrypt data using the global encryption instance."""
    return get_encryption().encrypt(data)

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data using the global encryption instance."""
    return get_encryption().decrypt(encrypted_data)

def encrypt_pii(data: str) -> str:
    """Encrypt PII using the global encryption instance."""
    return get_encryption().encrypt_pii(data)

def decrypt_pii(encrypted_data: str) -> str:
    """Decrypt PII using the global encryption instance."""
    return get_encryption().decrypt_pii(encrypted_data)

def create_search_hash(data: str) -> str:
    """Create search hash using the global encryption instance."""
    return get_encryption().create_hash_for_search(data)
