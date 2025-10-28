#!/usr/bin/env python3
"""
API Endpoint Integration Guide - Task 7 Authentication
Flask/Starlette endpoint examples for JWT and OAuth2 authentication
"""

import logging
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# FLASK ENDPOINT EXAMPLES
# ============================================================================

class AuthenticationAPI:
    """Authentication API endpoints"""

    @staticmethod
    def register_endpoints(app: Flask, auth_service, oauth2_service):
        """Register all auth endpoints on Flask app"""

        # ====================================================================
        # Authentication Endpoints
        # ====================================================================

        @app.route('/api/auth/register', methods=['POST'])
        def register():
            """Register new user"""
            data = request.get_json()

            # Validate input
            required = ['email', 'username', 'password', 'confirm_password', 'full_name']
            if not all(field in data for field in required):
                return jsonify({"error": "Missing required fields"}), 400

            # Check passwords match
            if data['password'] != data['confirm_password']:
                return jsonify({"error": "Passwords do not match"}), 400

            # Register user
            success, error, user_data = auth_service.register_user(
                email=data['email'],
                username=data['username'],
                password=data['password'],
                full_name=data['full_name']
            )

            if not success:
                return jsonify({"error": error}), 400

            logger.info(f"User registered: {data['email']}")
            return jsonify({
                "success": True,
                "message": "User registered successfully",
                "user": user_data
            }), 201

        @app.route('/api/auth/login', methods=['POST'])
        def login():
            """User login with JWT token generation"""
            data = request.get_json()

            # Validate input
            if 'email' not in data or 'password' not in data:
                return jsonify({"error": "Missing email or password"}), 400

            # Get IP and user agent
            ip_address = request.remote_addr or "unknown"
            user_agent = request.headers.get('User-Agent', '')

            # Authenticate user
            success, error, tokens = auth_service.authenticate_user(
                email=data['email'],
                password=data['password'],
                ip_address=ip_address,
                user_agent=user_agent
            )

            if not success:
                if error == "account_locked":
                    return jsonify({"error": "Account locked. Try again in 15 minutes"}), 429
                return jsonify({"error": error or "Authentication failed"}), 401

            logger.info(f"User logged in: {data['email']}")
            return jsonify({
                "success": True,
                "message": "Login successful",
                "access_token": tokens['access_token'],
                "refresh_token": tokens['refresh_token'],
                "expires_in": 1800  # 30 minutes in seconds
            }), 200

        @app.route('/api/auth/logout', methods=['POST'])
        def logout():
            """User logout - revoke token"""
            auth_header = request.headers.get('Authorization', '')

            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Missing authorization header"}), 401

            token = auth_header[7:]  # Remove 'Bearer '

            # Logout user
            success, error = auth_service.logout_user(token)

            if not success:
                return jsonify({"error": error}), 400

            logger.info("User logged out")
            return jsonify({"success": True, "message": "Logged out successfully"}), 200

        @app.route('/api/auth/refresh', methods=['POST'])
        def refresh_token():
            """Refresh access token"""
            data = request.get_json()

            if 'refresh_token' not in data:
                return jsonify({"error": "Missing refresh token"}), 400

            # Refresh token
            success, error, new_token = auth_service.refresh_token(
                refresh_token=data['refresh_token']
            )

            if not success:
                return jsonify({"error": error or "Token refresh failed"}), 401

            logger.info("Token refreshed")
            return jsonify({
                "success": True,
                "access_token": new_token,
                "expires_in": 1800
            }), 200

        @app.route('/api/auth/me', methods=['GET'])
        @require_auth
        def get_current_user(current_user):
            """Get current authenticated user"""
            return jsonify({
                "success": True,
                "user": {
                    "id": current_user["id"],
                    "email": current_user["email"],
                    "username": current_user["username"],
                    "full_name": current_user["full_name"],
                    "created_at": current_user["created_at"]
                }
            }), 200

        # ====================================================================
        # OAuth2 Endpoints
        # ====================================================================

        @app.route('/api/auth/google', methods=['GET'])
        def google_auth():
            """Initiate Google OAuth2 flow"""
            url, state = oauth2_service.google.get_authorization_url()

            # Store state in session (in production, use session or cache)
            # session['oauth_state'] = state

            return jsonify({
                "success": True,
                "authorization_url": url,
                "state": state
            }), 200

        @app.route('/api/auth/google/callback', methods=['POST'])
        def google_callback():
            """Google OAuth2 callback"""
            data = request.get_json()

            # Validate state
            if 'state' not in data or 'code' not in data:
                return jsonify({"error": "Missing state or code"}), 400

            # Verify state
            if not oauth2_service.validate_state(data['state'], 'google'):
                return jsonify({"error": "Invalid state"}), 401

            # Exchange code for token
            tokens = oauth2_service.google.get_access_token(data['code'])

            # Get user info
            user_info = oauth2_service.google.get_user_info(tokens['access_token'])

            # Create or update user in database
            user = auth_service.get_or_create_oauth_user(
                provider='google',
                provider_id=user_info['id'],
                email=user_info['email'],
                full_name=user_info.get('name', '')
            )

            # Generate JWT tokens
            access_token, _ = auth_service.generate_jwt_token(user['id'])
            refresh_token, _ = auth_service.generate_jwt_token(
                user['id'],
                token_type='refresh'
            )

            logger.info(f"Google OAuth login: {user_info['email']}")
            return jsonify({
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user
            }), 200

        @app.route('/api/auth/github', methods=['GET'])
        def github_auth():
            """Initiate GitHub OAuth2 flow"""
            url, state = oauth2_service.github.get_authorization_url()

            return jsonify({
                "success": True,
                "authorization_url": url,
                "state": state
            }), 200

        @app.route('/api/auth/github/callback', methods=['POST'])
        def github_callback():
            """GitHub OAuth2 callback"""
            data = request.get_json()

            # Validate state
            if 'state' not in data or 'code' not in data:
                return jsonify({"error": "Missing state or code"}), 400

            if not oauth2_service.validate_state(data['state'], 'github'):
                return jsonify({"error": "Invalid state"}), 401

            # Exchange code for token
            tokens = oauth2_service.github.get_access_token(data['code'])

            # Get user info
            user_info = oauth2_service.github.get_user_info(tokens['access_token'])

            # Create or update user
            user = auth_service.get_or_create_oauth_user(
                provider='github',
                provider_id=str(user_info['id']),
                email=user_info.get('email', f"{user_info['login']}@github.com"),
                full_name=user_info.get('name', user_info['login'])
            )

            # Generate JWT tokens
            access_token, _ = auth_service.generate_jwt_token(user['id'])
            refresh_token, _ = auth_service.generate_jwt_token(
                user['id'],
                token_type='refresh'
            )

            logger.info(f"GitHub OAuth login: {user_info['login']}")
            return jsonify({
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user
            }), 200

        # ====================================================================
        # Session Management Endpoints
        # ====================================================================

        @app.route('/api/auth/sessions', methods=['GET'])
        @require_auth
        def get_sessions(current_user):
            """Get all active sessions for user"""
            from session_manager import SessionManager

            session_mgr = SessionManager(db=None)
            devices = session_mgr.get_session_devices(current_user['id'])

            return jsonify({
                "success": True,
                "sessions": devices
            }), 200

        @app.route('/api/auth/sessions/<int:session_id>', methods=['DELETE'])
        @require_auth
        def revoke_session(current_user, session_id):
            """Revoke specific session"""
            from session_manager import SessionManager

            session_mgr = SessionManager(db=None)
            session_mgr.revoke_session(session_id)

            logger.info(f"Session revoked: {session_id}")
            return jsonify({"success": True, "message": "Session revoked"}), 200

        @app.route('/api/auth/sessions/all', methods=['DELETE'])
        @require_auth
        def revoke_all_sessions(current_user):
            """Revoke all user sessions"""
            from session_manager import SessionManager

            session_mgr = SessionManager(db=None)
            session_mgr.revoke_all_sessions(current_user['id'])

            logger.info(f"All sessions revoked for user {current_user['id']}")
            return jsonify({"success": True, "message": "All sessions revoked"}), 200

        # ====================================================================
        # Two-Factor Authentication Endpoints
        # ====================================================================

        @app.route('/api/auth/2fa/enable', methods=['POST'])
        @require_auth
        def enable_2fa(current_user):
            """Enable two-factor authentication"""
            from session_manager import TwoFactorAuth

            twofa = TwoFactorAuth(db=None)
            result = twofa.enable_2fa(current_user['id'], method='totp')

            logger.info(f"2FA enabled for user {current_user['id']}")
            return jsonify({
                "success": True,
                "secret": result['secret'],
                "provisioning_uri": result['provisioning_uri'],
                "backup_codes": result['backup_codes']
            }), 200

        @app.route('/api/auth/2fa/verify', methods=['POST'])
        @require_auth
        def verify_2fa(current_user):
            """Verify and confirm 2FA setup"""
            data = request.get_json()

            if 'code' not in data or 'secret' not in data:
                return jsonify({"error": "Missing code or secret"}), 400

            from session_manager import TwoFactorAuth

            twofa = TwoFactorAuth(db=None)
            if twofa.verify_2fa_code(current_user['id'], data['code'], data['secret']):
                # Save 2FA settings
                logger.info(f"2FA verified for user {current_user['id']}")
                return jsonify({"success": True, "message": "2FA enabled"}), 200

            return jsonify({"error": "Invalid 2FA code"}), 400

        @app.route('/api/auth/2fa/disable', methods=['POST'])
        @require_auth
        def disable_2fa(current_user):
            """Disable two-factor authentication"""
            from session_manager import TwoFactorAuth

            twofa = TwoFactorAuth(db=None)
            twofa.disable_2fa(current_user['id'])

            logger.info(f"2FA disabled for user {current_user['id']}")
            return jsonify({"success": True, "message": "2FA disabled"}), 200

        # ====================================================================
        # Password Reset Endpoints
        # ====================================================================

        @app.route('/api/auth/password-reset/request', methods=['POST'])
        def request_password_reset():
            """Request password reset"""
            data = request.get_json()

            if 'email' not in data:
                return jsonify({"error": "Missing email"}), 400

            from password_reset import PasswordResetService

            reset_service = PasswordResetService()
            # Get user by email (would query database)
            user_id = 123  # Placeholder

            success, token, message = reset_service.generate_reset_token(
                user_id,
                data['email']
            )

            if not success:
                return jsonify({"error": message}), 400

            # Send reset email
            reset_url = f"https://yourdomain.com/reset-password?token={token}"
            reset_service.send_reset_email(data['email'], reset_url)

            logger.info(f"Password reset requested: {data['email']}")
            return jsonify({
                "success": True,
                "message": "Reset link sent to email"
            }), 200

        @app.route('/api/auth/password-reset', methods=['POST'])
        def reset_password():
            """Reset password with token"""
            data = request.get_json()

            required = ['token', 'new_password', 'confirm_password']
            if not all(field in data for field in required):
                return jsonify({"error": "Missing required fields"}), 400

            from password_reset import PasswordResetService

            reset_service = PasswordResetService()
            success, error_type, message = reset_service.reset_password(
                data['token'],
                data['new_password'],
                data['confirm_password']
            )

            if not success:
                return jsonify({"error": message}), 400

            logger.info("Password reset successful")
            return jsonify({
                "success": True,
                "message": "Password reset successfully"
            }), 200

        # ====================================================================
        # Health Check
        # ====================================================================

        @app.route('/api/auth/health', methods=['GET'])
        def auth_health():
            """Check authentication service health"""
            return jsonify({
                "success": True,
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }), 200


# ============================================================================
# DECORATORS
# ============================================================================

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing authorization header"}), 401

        token = auth_header[7:]  # Remove 'Bearer '

        # Verify token (would use auth_service)
        try:
            # decoded = auth_service.decode_jwt_token(token)
            current_user = {
                "id": 123,
                "email": "user@example.com",
                "username": "username"
            }
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401

    return decorated_function


def require_scope(*scopes):
    """Decorator to require specific scopes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')

            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Missing authorization header"}), 401

            token = auth_header[7:]

            # Verify scopes (would decode and check)
            try:
                # decoded = auth_service.decode_jwt_token(token)
                # Check if required scopes present
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": "Insufficient permissions"}), 403

        return decorated_function

    return decorator


# ============================================================================
# INITIALIZATION
# ============================================================================

def setup_auth_endpoints(app: Flask, auth_service, oauth2_service):
    """Setup all authentication endpoints on Flask app"""
    api = AuthenticationAPI()
    api.register_endpoints(app, auth_service, oauth2_service)
    logger.info("Authentication endpoints registered")
