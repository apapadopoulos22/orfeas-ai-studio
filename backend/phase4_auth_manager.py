#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4.6 API KEY & AUTHENTICATION MANAGER
Security Layer for API Access Control

Manages API keys, authentication, and authorization

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4.6 IMPLEMENTATION
"""

import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import uuid

logger = logging.getLogger(__name__)


class APIKey:
    """Represents an API key with metadata"""

    def __init__(
        self,
        key: str,
        name: str,
        scopes: List[str] = None,
        rate_limit: int = 100,
        active: bool = True,
        created_at: datetime = None,
        expires_at: Optional[datetime] = None
    ):
        self.key = key
        self.name = name
        self.scopes = scopes or ['read:disciplines', 'read:graph', 'read:statistics']
        self.rate_limit = rate_limit  # requests per minute
        self.active = active
        self.created_at = created_at or datetime.utcnow()
        self.expires_at = expires_at  # None = never expires
        self.last_used = None
        self.usage_count = 0

    def is_valid(self) -> bool:
        """Check if API key is valid"""
        if not self.active:
            return False

        if self.expires_at and self.expires_at < datetime.utcnow():
            return False

        return True

    def has_scope(self, scope: str) -> bool:
        """Check if key has required scope"""
        return scope in self.scopes

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'name': self.name,
            'scopes': self.scopes,
            'rate_limit': self.rate_limit,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }


class AuthenticationManager:
    """Manages API key authentication"""

    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.key_hashes: Dict[str, str] = {}  # Maps hashes to key IDs
        logger.info("Initialized authentication manager")

        # Initialize with default development key
        self._init_default_keys()

    def _init_default_keys(self):
        """Initialize default development keys"""
        # Development key (unrestricted)
        dev_key = self.create_key(
            name="Development Key",
            scopes=['read:disciplines', 'read:graph', 'read:statistics', 'write:*'],
            rate_limit=1000,
            expires_at=None
        )
        logger.info(f"Development API key: {dev_key}")

        # Read-only key
        readonly_key = self.create_key(
            name="Read-Only Key",
            scopes=['read:disciplines', 'read:graph', 'read:statistics'],
            rate_limit=500,
            expires_at=None
        )
        logger.info(f"Read-only API key: {readonly_key}")

    def generate_api_key(self) -> str:
        """Generate a secure random API key"""
        return f"bob_ai_{secrets.token_urlsafe(32)}"

    def hash_key(self, key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def create_key(
        self,
        name: str,
        scopes: List[str] = None,
        rate_limit: int = 100,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Create a new API key"""
        key = self.generate_api_key()
        key_hash = self.hash_key(key)

        api_key = APIKey(
            key=key,
            name=name,
            scopes=scopes or ['read:disciplines', 'read:graph', 'read:statistics'],
            rate_limit=rate_limit,
            expires_at=expires_at
        )

        key_id = str(uuid.uuid4())
        self.api_keys[key_id] = api_key
        self.key_hashes[key_hash] = key_id

        logger.info(f"Created API key: {name} ({key_id})")
        return key

    def authenticate(self, api_key: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Authenticate an API key

        Returns:
            Tuple of (is_valid, key_id, api_key_data)
        """
        if not api_key:
            return False, None, None

        key_hash = self.hash_key(api_key)

        if key_hash not in self.key_hashes:
            logger.warning(f"Authentication attempt with invalid key")
            return False, None, None

        key_id = self.key_hashes[key_hash]
        api_key_obj = self.api_keys.get(key_id)

        if not api_key_obj:
            return False, None, None

        if not api_key_obj.is_valid():
            logger.warning(f"Authentication attempt with inactive/expired key: {key_id}")
            return False, None, None

        # Update usage stats
        api_key_obj.last_used = datetime.utcnow()
        api_key_obj.usage_count += 1

        logger.debug(f"Authentication successful: {key_id}")
        return True, key_id, api_key_obj.to_dict()

    def get_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        return self.api_keys.get(key_id)

    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id not in self.api_keys:
            return False

        self.api_keys[key_id].active = False
        logger.info(f"Revoked API key: {key_id}")
        return True

    def list_keys(self, include_inactive: bool = False) -> List[Dict]:
        """List all API keys"""
        keys = []
        for key_id, api_key in self.api_keys.items():
            if not include_inactive and not api_key.active:
                continue

            key_dict = api_key.to_dict()
            key_dict['key_id'] = key_id
            # Don't expose full key in listings
            key_dict['key'] = f"{key_dict['key'][:10]}...{key_dict['key'][-4:]}"
            keys.append(key_dict)

        return keys

    def check_scope(self, key_id: str, required_scope: str) -> bool:
        """Check if a key has the required scope"""
        api_key = self.get_key(key_id)
        if not api_key:
            return False

        # Admin scopes grant all access
        if 'admin:*' in api_key.scopes or 'write:*' in api_key.scopes:
            return True

        return api_key.has_scope(required_scope)

    def get_stats(self) -> Dict:
        """Get authentication statistics"""
        total_keys = len(self.api_keys)
        active_keys = sum(1 for k in self.api_keys.values() if k.active)
        expired_keys = sum(1 for k in self.api_keys.values() if k.expires_at and k.expires_at < datetime.utcnow())

        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'inactive_keys': total_keys - active_keys,
            'expired_keys': expired_keys,
            'total_requests': sum(k.usage_count for k in self.api_keys.values())
        }


def get_auth_manager() -> AuthenticationManager:
    """Get or create authentication manager singleton"""
    if not hasattr(get_auth_manager, '_instance'):
        get_auth_manager._instance = AuthenticationManager()
    return get_auth_manager._instance


if __name__ == '__main__':
    # Test authentication manager
    logging.basicConfig(level=logging.INFO)

    auth = get_auth_manager()

    # Create test key
    test_key = auth.create_key(
        name="Test Key",
        scopes=['read:disciplines'],
        rate_limit=50,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    print(f"Created test key: {test_key}")

    # Authenticate
    is_valid, key_id, key_data = auth.authenticate(test_key)
    print(f"Authentication result: valid={is_valid}, key_id={key_id}")

    # List keys
    print(f"Active keys: {auth.list_keys()}")

    # Stats
    print(f"Auth stats: {auth.get_stats()}")
