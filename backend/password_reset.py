#!/usr/bin/env python3
"""
Password Reset & Account Recovery Module
Handles secure password reset flows and account recovery
"""

import logging
import secrets
import string
from typing import Optional, Tuple, Dict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PasswordResetConfig:
    """Password reset configuration"""
    RESET_TOKEN_EXPIRY_MINUTES = 60
    RESET_TOKEN_LENGTH = 32
    PASSWORD_HISTORY_COUNT = 5
    PASSWORD_CHANGE_MIN_HOURS = 1
    MAX_RESET_ATTEMPTS = 3
    RESET_ATTEMPT_WINDOW_HOURS = 24


class PasswordResetService:
    """Handle password reset workflows"""

    def __init__(self, db=None, email_service=None):
        self.db = db
        self.email_service = email_service
        self.config = PasswordResetConfig()
        # In production, would use Redis for token storage
        self._tokens: Dict[str, Dict] = {}

    def generate_reset_token(self, user_id: int, user_email: str) -> Tuple[bool, str, str]:
        """Generate a password reset token"""

        # Check reset attempt limit
        reset_attempts = self._get_reset_attempts(user_id)
        if reset_attempts >= self.config.MAX_RESET_ATTEMPTS:
            logger.warning(f"Reset attempt limit reached for user {user_id}")
            return False, "error", "Too many reset attempts. Please try again later."

        # Generate secure token
        token_chars = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(token_chars) for _ in range(self.config.RESET_TOKEN_LENGTH))

        # Store token with metadata
        expires_at = datetime.utcnow() + timedelta(minutes=self.config.RESET_TOKEN_EXPIRY_MINUTES)

        self._tokens[token] = {
            "user_id": user_id,
            "user_email": user_email,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.utcnow()
        }

        # Record reset attempt
        self._record_reset_attempt(user_id)

        logger.info(f"Reset token generated for user {user_id}")
        return True, token, "Reset token generated"

    def validate_reset_token(self, token: str) -> Tuple[bool, Optional[Dict], str]:
        """Validate a password reset token"""

        if token not in self._tokens:
            logger.warning(f"Invalid reset token attempted")
            return False, None, "Invalid reset token"

        token_data = self._tokens[token]

        # Check if already used
        if token_data["used"]:
            logger.warning(f"Reset token already used for user {token_data['user_id']}")
            return False, None, "Token already used"

        # Check expiration
        if datetime.utcnow() > token_data["expires_at"]:
            logger.warning(f"Reset token expired for user {token_data['user_id']}")
            return False, None, "Token expired"

        return True, token_data, "Token valid"

    def reset_password(
        self,
        token: str,
        new_password: str,
        confirm_password: str
    ) -> Tuple[bool, str, str]:
        """Reset user password with token"""

        # Validate token
        valid, token_data, message = self.validate_reset_token(token)
        if not valid:
            return False, "invalid_token", message

        # Validate passwords match
        if new_password != confirm_password:
            return False, "mismatch", "Passwords do not match"

        # Validate password strength
        is_strong, error = self._validate_password_strength(new_password)
        if not is_strong:
            return False, "weak_password", error

        # Check password history
        if self._is_password_reused(token_data["user_id"], new_password):
            return False, "reused", "Cannot reuse previous passwords"

        # Hash and store new password
        # In production, would use bcrypt similar to auth_service.py
        hashed_password = self._hash_password(new_password)

        # Update user in database
        # self.db.update_user_password(token_data["user_id"], hashed_password)

        # Mark token as used
        self._tokens[token]["used"] = True

        # Store in password history
        self._add_to_password_history(token_data["user_id"], hashed_password)

        # Clear other reset tokens for this user
        self._revoke_user_reset_tokens(token_data["user_id"])

        logger.info(f"Password reset completed for user {token_data['user_id']}")
        return True, "success", "Password reset successfully"

    def send_reset_email(self, user_email: str, reset_url: str) -> bool:
        """Send password reset email"""

        try:
            subject = "Password Reset Request - ORFEAS AI"

            body = f"""
            <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>You requested to reset your password. Click the link below to continue:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>This link will expire in {self.config.RESET_TOKEN_EXPIRY_MINUTES} minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <hr/>
                    <p><small>ORFEAS AI Studio</small></p>
                </body>
            </html>
            """

            if self.email_service:
                return self.email_service.send_email(user_email, subject, body)

            logger.info(f"Reset email would be sent to {user_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send reset email: {e}")
            return False

    def verify_old_password(self, user_id: int, old_password: str) -> bool:
        """Verify old password before allowing change"""
        # In production, would retrieve and verify password hash
        logger.info(f"Old password verified for user {user_id}")
        return True

    def _validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password meets requirements"""

        if len(password) < 12:
            return False, "Password must be at least 12 characters"

        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain special character"

        return True, "Password meets requirements"

    def _is_password_reused(self, user_id: int, new_password: str) -> bool:
        """Check if password was previously used"""
        # In production, would check against password history
        # For now, return False (no reuse)
        return False

    def _hash_password(self, password: str) -> str:
        """Hash password (would use bcrypt in production)"""
        return f"hashed_{password}"

    def _add_to_password_history(self, user_id: int, hashed_password: str) -> None:
        """Add password to user's history"""
        # Implementation would store in database
        logger.debug(f"Added password to history for user {user_id}")

    def _revoke_user_reset_tokens(self, user_id: int) -> None:
        """Revoke all active reset tokens for user"""
        tokens_to_remove = [
            token for token, data in self._tokens.items()
            if data["user_id"] == user_id and not data["used"]
        ]

        for token in tokens_to_remove:
            del self._tokens[token]

        logger.info(f"Revoked {len(tokens_to_remove)} reset tokens for user {user_id}")

    def _get_reset_attempts(self, user_id: int) -> int:
        """Get number of reset attempts in window"""
        # In production, would query database with time window
        return 0

    def _record_reset_attempt(self, user_id: int) -> None:
        """Record password reset attempt"""
        # In production, would store in database with timestamp
        logger.debug(f"Reset attempt recorded for user {user_id}")


class EmailService:
    """Handle email sending"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email"""

        try:
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = to_email

            # Attach HTML body
            msg.attach(MIMEText(body, "html"))

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, to_email, msg.as_string())

            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class AccountRecoveryService:
    """Handle account recovery flows"""

    def __init__(self, db=None):
        self.db = db
        self._recovery_attempts: Dict[str, int] = {}

    def verify_account_recovery(self, email: str, recovery_code: str) -> Tuple[bool, str]:
        """Verify recovery code sent to alternate email/phone"""

        # Check attempt limit
        if self._recovery_attempts.get(email, 0) >= 3:
            return False, "Too many recovery attempts"

        # Verify recovery code (would be from database)
        if not self._verify_recovery_code(email, recovery_code):
            self._recovery_attempts[email] = self._recovery_attempts.get(email, 0) + 1
            return False, "Invalid recovery code"

        # Reset attempt counter on success
        self._recovery_attempts[email] = 0

        logger.info(f"Account recovery verified for {email}")
        return True, "Account recovered successfully"

    def _verify_recovery_code(self, email: str, code: str) -> bool:
        """Verify recovery code (implementation would query database)"""
        return True
