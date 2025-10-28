#!/usr/bin/env python3
"""
OAuth2 Integration Module
Provides OAuth2 support for Google, GitHub, and custom OAuth providers
"""

import os
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime
import requests
from urllib.parse import urlencode
import secrets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OAuth2Config:
    """OAuth2 configuration"""

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    # GitHub OAuth
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:5000/auth/github/callback")
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USERINFO_URL = "https://api.github.com/user"

    # OAuth state timeout (seconds)
    STATE_TIMEOUT = 600


class OAuth2StateManager:
    """Manage OAuth2 state tokens for CSRF protection"""

    def __init__(self):
        self.states: Dict[str, Dict] = {}  # In production, use Redis

    def generate_state(self, provider: str) -> str:
        """Generate and store state token"""
        state = secrets.token_urlsafe(32)
        self.states[state] = {
            "provider": provider,
            "created_at": datetime.utcnow()
        }
        return state

    def validate_state(self, state: str, provider: str) -> bool:
        """Validate state token"""
        if state not in self.states:
            logger.warning(f"Invalid state token: {state}")
            return False

        state_data = self.states[state]

        # Check provider
        if state_data["provider"] != provider:
            logger.warning(f"State provider mismatch: expected {provider}, got {state_data['provider']}")
            return False

        # Check timeout
        created_at = state_data["created_at"]
        age = (datetime.utcnow() - created_at).total_seconds()
        if age > OAuth2Config.STATE_TIMEOUT:
            logger.warning(f"State token expired: {age}s old")
            del self.states[state]
            return False

        # Clean up
        del self.states[state]
        return True


class OAuth2Provider:
    """Base OAuth2 provider"""

    def __init__(self, db_session):
        self.db = db_session
        self.state_manager = OAuth2StateManager()

    def get_authorization_url(self, provider: str) -> Tuple[str, str]:
        """Get OAuth2 authorization URL"""
        raise NotImplementedError

    def get_access_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        raise NotImplementedError

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from OAuth2 provider"""
        raise NotImplementedError

    def authenticate_user(self, provider_user_id: str, email: str, name: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Authenticate or create user from OAuth2 provider"""
        raise NotImplementedError


class GoogleOAuth2(OAuth2Provider):
    """Google OAuth2 provider"""

    def get_authorization_url(self) -> Tuple[str, str]:
        """Get Google authorization URL"""
        state = self.state_manager.generate_state("google")

        params = {
            "client_id": OAuth2Config.GOOGLE_CLIENT_ID,
            "redirect_uri": OAuth2Config.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account"
        }

        url = f"{OAuth2Config.GOOGLE_AUTH_URL}?{urlencode(params)}"
        return url, state

    def get_access_token(self, code: str) -> Optional[Dict]:
        """Exchange Google authorization code for access token"""
        try:
            response = requests.post(
                OAuth2Config.GOOGLE_TOKEN_URL,
                data={
                    "client_id": OAuth2Config.GOOGLE_CLIENT_ID,
                    "client_secret": OAuth2Config.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": OAuth2Config.GOOGLE_REDIRECT_URI
                },
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Google token exchange failed: {response.text}")
                return None

            return response.json()
        except Exception as e:
            logger.error(f"Google token exchange error: {e}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from Google"""
        try:
            response = requests.get(
                OAuth2Config.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Google user info failed: {response.text}")
                return None

            return response.json()
        except Exception as e:
            logger.error(f"Google user info error: {e}")
            return None


class GitHubOAuth2(OAuth2Provider):
    """GitHub OAuth2 provider"""

    def get_authorization_url(self) -> Tuple[str, str]:
        """Get GitHub authorization URL"""
        state = self.state_manager.generate_state("github")

        params = {
            "client_id": OAuth2Config.GITHUB_CLIENT_ID,
            "redirect_uri": OAuth2Config.GITHUB_REDIRECT_URI,
            "scope": "user:email",
            "state": state,
            "allow_signup": "true"
        }

        url = f"{OAuth2Config.GITHUB_AUTH_URL}?{urlencode(params)}"
        return url, state

    def get_access_token(self, code: str) -> Optional[Dict]:
        """Exchange GitHub authorization code for access token"""
        try:
            response = requests.post(
                OAuth2Config.GITHUB_TOKEN_URL,
                data={
                    "client_id": OAuth2Config.GITHUB_CLIENT_ID,
                    "client_secret": OAuth2Config.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": OAuth2Config.GITHUB_REDIRECT_URI
                },
                headers={"Accept": "application/json"},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.text}")
                return None

            return response.json()
        except Exception as e:
            logger.error(f"GitHub token exchange error: {e}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from GitHub"""
        try:
            response = requests.get(
                OAuth2Config.GITHUB_USERINFO_URL,
                headers={"Authorization": f"token {access_token}"},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"GitHub user info failed: {response.text}")
                return None

            return response.json()
        except Exception as e:
            logger.error(f"GitHub user info error: {e}")
            return None


class OAuth2Manager:
    """Manage OAuth2 authentication"""

    def __init__(self, db_session):
        self.db = db_session
        self.google = GoogleOAuth2(db_session)
        self.github = GitHubOAuth2(db_session)

    def get_provider(self, provider_name: str) -> Optional[OAuth2Provider]:
        """Get OAuth2 provider by name"""
        providers = {
            "google": self.google,
            "github": self.github
        }
        return providers.get(provider_name)

    def validate_state(self, state: str, provider: str) -> bool:
        """Validate OAuth2 state token"""
        provider_obj = self.get_provider(provider)
        if not provider_obj:
            return False

        return provider_obj.state_manager.validate_state(state, provider)
