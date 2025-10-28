#!/usr/bin/env python3
"""
User Authentication Module - JWT and OAuth2 Integration
Provides secure authentication, token management, and session handling
Integrates with Task 4 PostgreSQL database
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from functools import wraps
import hashlib
import secrets

import jwt
from sqlalchemy import Column, String, DateTime, Boolean, Integer, LargeBinary
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class AuthConfig:
    """Authentication configuration"""
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    RESET_TOKEN_EXPIRE_HOURS = 1
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True


# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


# Database Models
class UserModel:
    """SQLAlchemy User model for Task 4 database integration"""

    def __init__(self):
        self.id = Column(Integer, primary_key=True, index=True)
        self.email = Column(String(255), unique=True, index=True, nullable=False)
        self.username = Column(String(100), unique=True, index=True, nullable=False)
        self.full_name = Column(String(255))
        self.hashed_password = Column(String(255), nullable=False)
        self.is_active = Column(Boolean, default=True, index=True)
        self.is_verified = Column(Boolean, default=False)
        self.created_at = Column(DateTime, default=datetime.utcnow, index=True)
        self.updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        self.last_login = Column(DateTime, nullable=True)
        self.login_attempts = Column(Integer, default=0)
        self.locked_until = Column(DateTime, nullable=True)
        self.two_factor_enabled = Column(Boolean, default=False)
        self.two_factor_secret = Column(String(32), nullable=True)


class SessionModel:
    """SQLAlchemy Session model for tracking active sessions"""

    def __init__(self):
        self.id = Column(Integer, primary_key=True, index=True)
        self.user_id = Column(Integer, index=True, nullable=False)
        self.token_jti = Column(String(255), unique=True, index=True, nullable=False)
        self.refresh_token_jti = Column(String(255), unique=True, index=True, nullable=True)
        self.ip_address = Column(String(45))
        self.user_agent = Column(String(500))
        self.created_at = Column(DateTime, default=datetime.utcnow, index=True)
        self.expires_at = Column(DateTime, nullable=False, index=True)
        self.revoked = Column(Boolean, default=False, index=True)


class TokenBlocklistModel:
    """SQLAlchemy model for maintaining token blocklist"""

    def __init__(self):
        self.id = Column(Integer, primary_key=True, index=True)
        self.jti = Column(String(255), unique=True, index=True, nullable=False)
        self.token_type = Column(String(20))  # 'access' or 'refresh'
        self.user_id = Column(Integer, index=True, nullable=False)
        self.blocked_at = Column(DateTime, default=datetime.utcnow, index=True)
        self.expires_at = Column(DateTime, nullable=False, index=True)


# Pydantic Models for validation
class UserBase(BaseModel):
    """Base user model for API"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserRegister(UserBase):
    """User registration model"""
    password: str = Field(..., min_length=AuthConfig.PASSWORD_MIN_LENGTH)

    def validate_password(self) -> Tuple[bool, Optional[str]]:
        """Validate password meets requirements"""
        if AuthConfig.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in self.password):
            return False, "Password must contain uppercase letter"
        if AuthConfig.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in self.password):
            return False, "Password must contain number"
        if AuthConfig.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*" for c in self.password):
            return False, "Password must contain special character (!@#$%^&*)"
        return True, None


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    scope: str = "read write"


class UserResponse(UserBase):
    """User response model"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# Authentication Service
class AuthenticationService:
    """Core authentication service"""

    def __init__(self, db: Session):
        self.db = db
        self.config = AuthConfig()

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def generate_jwt_token(
        self,
        user_id: int,
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
    ) -> Tuple[str, str]:
        """Generate JWT token with unique JTI"""
        if expires_delta is None:
            if token_type == "access":
                expires_delta = timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
            else:
                expires_delta = timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)

        # Generate unique JTI (JWT ID)
        jti = secrets.token_urlsafe(32)

        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": token_type
        }

        token = jwt.encode(
            payload,
            self.config.JWT_SECRET_KEY,
            algorithm=self.config.JWT_ALGORITHM
        )

        return token, jti

    def decode_jwt_token(self, token: str) -> Optional[Dict]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM]
            )

            # Check if token is in blocklist
            jti = payload.get("jti")
            if jti and self._is_token_blocked(jti):
                logger.warning(f"Attempt to use blocked token: {jti}")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def _is_token_blocked(self, jti: str) -> bool:
        """Check if token JTI is in blocklist"""
        # Implementation would query TokenBlocklistModel
        # For now, return False
        return False

    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Register new user"""
        # Check if user exists
        existing = self.db.query(UserModel).filter(
            (UserModel.email == email) | (UserModel.username == username)
        ).first()

        if existing:
            return False, "User already exists", None

        try:
            # Hash password
            hashed_password = self.hash_password(password)

            # Create user
            user = UserModel(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hashed_password
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"User registered: {email}")
            return True, None, {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e}")
            return False, str(e), None

    def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: str = "0.0.0.0",
        user_agent: str = ""
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Authenticate user and return tokens"""
        # Find user
        user = self.db.query(UserModel).filter(UserModel.email == email).first()

        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return False, "Invalid credentials", None

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = (user.locked_until - datetime.utcnow()).total_seconds() / 60
            return False, f"Account locked. Try again in {remaining:.0f} minutes", None

        # Check if user is active
        if not user.is_active:
            return False, "Account is inactive", None

        # Verify password
        if not self.verify_password(password, user.hashed_password):
            # Increment login attempts
            user.login_attempts += 1

            if user.login_attempts >= self.config.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=self.config.LOCKOUT_DURATION_MINUTES
                )
                self.db.commit()
                return False, "Too many login attempts. Account locked", None

            self.db.commit()
            return False, "Invalid credentials", None

        # Reset login attempts
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Generate tokens
        access_token, access_jti = self.generate_jwt_token(user.id, token_type="access")
        refresh_token, refresh_jti = self.generate_jwt_token(user.id, token_type="refresh")

        # Store session
        self._create_session(user.id, access_jti, refresh_jti, ip_address, user_agent)

        logger.info(f"User authenticated: {email}")

        return True, None, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }

    def _create_session(
        self,
        user_id: int,
        access_jti: str,
        refresh_jti: str,
        ip_address: str,
        user_agent: str
    ) -> None:
        """Create session record"""
        expires_at = datetime.utcnow() + timedelta(
            minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        session = SessionModel(
            user_id=user_id,
            token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )

        self.db.add(session)
        self.db.commit()

    def refresh_token(self, refresh_token: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Refresh access token"""
        payload = self.decode_jwt_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return False, "Invalid refresh token", None

        user_id = int(payload.get("sub"))

        # Generate new access token
        access_token, access_jti = self.generate_jwt_token(user_id, token_type="access")

        return True, None, {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def logout_user(self, token: str, token_type: str = "access") -> Tuple[bool, Optional[str]]:
        """Logout user by blocking token"""
        payload = self.decode_jwt_token(token)

        if not payload:
            return False, "Invalid token"

        jti = payload.get("jti")
        user_id = int(payload.get("sub"))
        expires_at = datetime.fromtimestamp(payload.get("exp"))

        # Add to blocklist
        blocklist_entry = TokenBlocklistModel(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at
        )

        self.db.add(blocklist_entry)
        self.db.commit()

        logger.info(f"User logged out: {user_id}")
        return True, None


# Flask/Starlette Decorators
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header[7:]  # Remove "Bearer " prefix

        auth_service = AuthenticationService(db=None)  # Get from context
        payload = auth_service.decode_jwt_token(token)

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user_id = int(payload.get("sub"))
        return f(*args, **kwargs)

    return decorated_function


def require_scope(required_scopes: List[str]):
    """Decorator to require specific scopes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify

            # Implementation for scope checking
            user_scopes = getattr(request, "scopes", [])

            if not any(scope in user_scopes for scope in required_scopes):
                return jsonify({"error": "Insufficient permissions"}), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator
