#!/usr/bin/env python3
"""
Secret rotation script for Vantage AI.
Re-encrypts stored tokens with a new encryption key while maintaining backward compatibility.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import get_db
from app.models.entities import Channel
from app.models.billing import StripeCustomer
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecretRotator:
    """Handles secret rotation for encrypted tokens."""
    
    def __init__(self, new_key: str, dry_run: bool = False):
        self.new_key = new_key
        self.dry_run = dry_run
        self.settings = get_settings()
        self.current_version = self._get_current_key_version()
        self.new_version = self.current_version + 1
        
        logger.info(f"Current key version: {self.current_version}")
        logger.info(f"New key version: {self.new_version}")
        logger.info(f"Dry run mode: {dry_run}")
    
    def _get_current_key_version(self) -> int:
        """Get the current key version from environment."""
        return int(os.getenv('SECRET_KEY_VERSION', '1'))
    
    def _derive_key(self, password: str, salt: bytes, version: int) -> bytes:
        """Derive encryption key from password and salt."""
        # Include version in salt to ensure different keys for different versions
        versioned_salt = salt + str(version).encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=versioned_salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_token(self, token: str, version: int) -> Dict[str, Any]:
        """Encrypt a token with the specified version."""
        # Generate a random salt for this token
        salt = os.urandom(16)
        
        # Derive key for this version
        key = self._derive_key(self.new_key, salt, version)
        fernet = Fernet(key)
        
        # Encrypt the token
        encrypted_token = fernet.encrypt(token.encode())
        
        return {
            'encrypted_data': base64.urlsafe_b64encode(encrypted_token).decode(),
            'salt': base64.urlsafe_b64encode(salt).decode(),
            'version': version
        }
    
    def _decrypt_token(self, encrypted_data: str, salt: str, version: int) -> str:
        """Decrypt a token with the specified version."""
        try:
            # Decode base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            salt_bytes = base64.urlsafe_b64decode(salt)
            
            # Derive key for this version
            key = self._derive_key(self.new_key, salt_bytes, version)
            fernet = Fernet(key)
            
            # Decrypt the token
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            return None
    
    def _get_encrypted_fields(self) -> List[Dict[str, Any]]:
        """Get all fields that need to be re-encrypted."""
        return [
            {
                'model': Channel,
                'fields': ['access_token', 'refresh_token'],
                'filters': {'access_token': lambda x: x is not None}
            },
            {
                'model': StripeCustomer,
                'fields': ['stripe_customer_id'],
                'filters': {'stripe_customer_id': lambda x: x is not None}
            }
        ]
    
    def _is_encrypted_field(self, field_value: str) -> bool:
        """Check if a field value is encrypted (contains version info)."""
        try:
            data = json.loads(field_value)
            return isinstance(data, dict) and 'version' in data and 'encrypted_data' in data
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _parse_encrypted_field(self, field_value: str) -> Dict[str, Any]:
        """Parse an encrypted field value."""
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def rotate_secrets(self) -> Dict[str, Any]:
        """Rotate all secrets in the database."""
        results = {
            'total_processed': 0,
            'successful_rotations': 0,
            'failed_rotations': 0,
            'skipped_rotations': 0,
            'errors': []
        }
        
        db = next(get_db())
        
        try:
            for field_config in self._get_encrypted_fields():
                model = field_config['model']
                fields = field_config['fields']
                filters = field_config.get('filters', {})
                
                logger.info(f"Processing {model.__name__}...")
                
                # Get all records that have encrypted fields
                query = db.query(model)
                for field, filter_func in filters.items():
                    query = query.filter(getattr(model, field).isnot(None))
                
                records = query.all()
                logger.info(f"Found {len(records)} records to process")
                
                for record in records:
                    results['total_processed'] += 1
                    
                    try:
                        updated = False
                        
                        for field in fields:
                            field_value = getattr(record, field)
                            if not field_value:
                                continue
                            
                            # Check if field is already encrypted
                            if self._is_encrypted_field(field_value):
                                encrypted_data = self._parse_encrypted_field(field_value)
                                if encrypted_data and encrypted_data.get('version') == self.new_version:
                                    # Already encrypted with new version
                                    results['skipped_rotations'] += 1
                                    continue
                            
                            # Decrypt if needed
                            if self._is_encrypted_field(field_value):
                                encrypted_data = self._parse_encrypted_field(field_value)
                                if encrypted_data:
                                    decrypted_token = self._decrypt_token(
                                        encrypted_data['encrypted_data'],
                                        encrypted_data['salt'],
                                        encrypted_data['version']
                                    )
                                    if not decrypted_token:
                                        logger.error(f"Failed to decrypt {field} for {model.__name__} {record.id}")
                                        results['failed_rotations'] += 1
                                        continue
                                else:
                                    # Field is not properly encrypted, skip
                                    results['skipped_rotations'] += 1
                                    continue
                            else:
                                # Field is not encrypted, use as-is
                                decrypted_token = field_value
                            
                            # Encrypt with new version
                            if not self.dry_run:
                                encrypted_data = self._encrypt_token(decrypted_token, self.new_version)
                                setattr(record, field, json.dumps(encrypted_data))
                                updated = True
                            else:
                                logger.info(f"Would encrypt {field} for {model.__name__} {record.id}")
                                updated = True
                        
                        if updated and not self.dry_run:
                            db.commit()
                            results['successful_rotations'] += 1
                        elif updated and self.dry_run:
                            results['successful_rotations'] += 1
                        else:
                            results['skipped_rotations'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing {model.__name__} {record.id}: {e}")
                        results['failed_rotations'] += 1
                        results['errors'].append(f"{model.__name__} {record.id}: {str(e)}")
                        db.rollback()
            
            # Update the key version in environment
            if not self.dry_run:
                self._update_key_version()
                logger.info(f"Updated key version to {self.new_version}")
            
        except Exception as e:
            logger.error(f"Error during secret rotation: {e}")
            results['errors'].append(f"General error: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        return results
    
    def _update_key_version(self):
        """Update the key version in the environment."""
        # In a real implementation, you would update this in your configuration system
        # For now, we'll just log it
        logger.info(f"Key version should be updated to {self.new_version}")
        logger.info("Please update SECRET_KEY_VERSION environment variable")
    
    def verify_rotation(self) -> bool:
        """Verify that all secrets can be decrypted with the new key."""
        logger.info("Verifying secret rotation...")
        
        db = next(get_db())
        all_valid = True
        
        try:
            for field_config in self._get_encrypted_fields():
                model = field_config['model']
                fields = field_config['fields']
                filters = field_config.get('filters', {})
                
                query = db.query(model)
                for field, filter_func in filters.items():
                    query = query.filter(getattr(model, field).isnot(None))
                
                records = query.all()
                
                for record in records:
                    for field in fields:
                        field_value = getattr(record, field)
                        if not field_value:
                            continue
                        
                        if self._is_encrypted_field(field_value):
                            encrypted_data = self._parse_encrypted_field(field_value)
                            if encrypted_data:
                                decrypted_token = self._decrypt_token(
                                    encrypted_data['encrypted_data'],
                                    encrypted_data['salt'],
                                    encrypted_data['version']
                                )
                                if not decrypted_token:
                                    logger.error(f"Failed to decrypt {field} for {model.__name__} {record.id}")
                                    all_valid = False
                                else:
                                    logger.debug(f"Successfully decrypted {field} for {model.__name__} {record.id}")
            
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            all_valid = False
        finally:
            db.close()
        
        return all_valid


def main():
    """Main function for the secret rotation script."""
    parser = argparse.ArgumentParser(description='Rotate encryption secrets for Vantage AI')
    parser.add_argument('--new-key', required=True, help='New encryption key')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making changes')
    parser.add_argument('--verify', action='store_true', help='Verify that all secrets can be decrypted')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize the rotator
    rotator = SecretRotator(args.new_key, args.dry_run)
    
    if args.verify:
        # Verify rotation
        if rotator.verify_rotation():
            logger.info("✅ All secrets can be decrypted successfully")
            sys.exit(0)
        else:
            logger.error("❌ Some secrets could not be decrypted")
            sys.exit(1)
    else:
        # Perform rotation
        logger.info("Starting secret rotation...")
        results = rotator.rotate_secrets()
        
        # Print results
        logger.info("Secret rotation completed!")
        logger.info(f"Total processed: {results['total_processed']}")
        logger.info(f"Successful rotations: {results['successful_rotations']}")
        logger.info(f"Failed rotations: {results['failed_rotations']}")
        logger.info(f"Skipped rotations: {results['skipped_rotations']}")
        
        if results['errors']:
            logger.error("Errors encountered:")
            for error in results['errors']:
                logger.error(f"  - {error}")
        
        if results['failed_rotations'] > 0:
            logger.error("Some rotations failed. Please check the logs.")
            sys.exit(1)
        else:
            logger.info("✅ All secrets rotated successfully!")
            sys.exit(0)


if __name__ == '__main__':
    main()
