#!/usr/bin/env python3
"""
Session Management Module
Handles user sessions, device tracking, and concurrent session limits
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionConfig:
    """Session configuration"""
    MAX_CONCURRENT_SESSIONS = 5
    SESSION_TIMEOUT_MINUTES = 30
    REMEMBER_ME_DAYS = 30
    SESSION_REFRESH_MINUTES = 5


class SessionManager:
    """Manage user sessions"""

    def __init__(self, db: Session):
        self.db = db
        self.config = SessionConfig()

    def create_session(
        self,
        user_id: int,
        access_token: str,
        refresh_token: str,
        ip_address: str,
        user_agent: str,
        remember_me: bool = False
    ) -> Dict:
        """Create a new session"""

        # Check concurrent sessions
        active_sessions = self.get_active_sessions(user_id)

        if len(active_sessions) >= self.config.MAX_CONCURRENT_SESSIONS:
            # Revoke oldest session
            oldest = min(active_sessions, key=lambda s: s["created_at"])
            self.revoke_session(oldest["id"])
            logger.info(f"Revoked oldest session for user {user_id}")

        # Calculate expiration
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=self.config.REMEMBER_ME_DAYS)
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=self.config.SESSION_TIMEOUT_MINUTES)

        # Create session record (implementation would use database)
        session = {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "last_activity": datetime.utcnow(),
            "active": True,
            "remember_me": remember_me
        }

        logger.info(f"Session created for user {user_id}")
        return session

    def get_active_sessions(self, user_id: int) -> List[Dict]:
        """Get all active sessions for a user"""
        # Implementation would query database
        # For now, return empty list
        return []

    def validate_session(self, user_id: int, access_token: str) -> bool:
        """Validate if session is still active"""
        # Check token validity and session status
        # Implementation would query database
        return True

    def update_last_activity(self, user_id: int, access_token: str) -> None:
        """Update last activity timestamp"""
        # Implementation would update database
        logger.debug(f"Session activity updated for user {user_id}")

    def revoke_session(self, session_id: int) -> None:
        """Revoke a specific session"""
        # Implementation would mark session as revoked
        logger.info(f"Session revoked: {session_id}")

    def revoke_all_sessions(self, user_id: int) -> None:
        """Revoke all sessions for a user"""
        active_sessions = self.get_active_sessions(user_id)
        for session in active_sessions:
            self.revoke_session(session["id"])
        logger.info(f"All sessions revoked for user {user_id}")

    def get_session_devices(self, user_id: int) -> List[Dict]:
        """Get list of devices/sessions for user"""
        sessions = self.get_active_sessions(user_id)

        devices = []
        for session in sessions:
            devices.append({
                "id": session.get("id"),
                "user_agent": session.get("user_agent"),
                "ip_address": session.get("ip_address"),
                "created_at": session.get("created_at"),
                "last_activity": session.get("last_activity"),
                "current": False  # Would be set based on current session
            })

        return devices

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from database"""
        # Implementation would delete expired sessions
        logger.info("Cleaned up expired sessions")
        return 0


class DeviceTracker:
    """Track and manage user devices"""

    def __init__(self, db: Session):
        self.db = db

    def register_device(
        self,
        user_id: int,
        device_name: str,
        device_type: str,
        ip_address: str,
        user_agent: str
    ) -> Dict:
        """Register a new device"""
        device = {
            "user_id": user_id,
            "device_name": device_name,
            "device_type": device_type,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "registered_at": datetime.utcnow(),
            "last_used": datetime.utcnow(),
            "trusted": False
        }

        logger.info(f"Device registered for user {user_id}: {device_name}")
        return device

    def trust_device(self, user_id: int, device_id: int) -> bool:
        """Mark device as trusted (skip 2FA)"""
        # Implementation would update database
        logger.info(f"Device {device_id} trusted for user {user_id}")
        return True

    def untrust_device(self, user_id: int, device_id: int) -> bool:
        """Remove trust from device"""
        # Implementation would update database
        logger.info(f"Device {device_id} untrusted for user {user_id}")
        return True

    def get_user_devices(self, user_id: int) -> List[Dict]:
        """Get all devices for user"""
        # Implementation would query database
        return []

    def is_device_trusted(self, user_id: int, device_id: int) -> bool:
        """Check if device is trusted"""
        # Implementation would query database
        return False


class TwoFactorAuth:
    """Two-factor authentication management"""

    def __init__(self, db: Session):
        self.db = db

    def enable_2fa(self, user_id: int, method: str = "totp") -> Dict:
        """Enable two-factor authentication"""
        import pyotp

        if method == "totp":
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)

            # In production, also generate backup codes
            backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]

            return {
                "secret": secret,
                "provisioning_uri": totp.provisioning_uri(
                    name=f"ORFEAS:{user_id}",
                    issuer_name="ORFEAS AI"
                ),
                "backup_codes": backup_codes,
                "method": "totp"
            }

        return {}

    def verify_2fa_code(self, user_id: int, code: str, secret: str) -> bool:
        """Verify 2FA code"""
        import pyotp

        totp = pyotp.TOTP(secret)

        # Allow 30 second window on each side
        return totp.verify(code, valid_window=1)

    def disable_2fa(self, user_id: int) -> bool:
        """Disable two-factor authentication"""
        # Implementation would update database
        logger.info(f"2FA disabled for user {user_id}")
        return True
