from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from passlib.hash import pbkdf2_sha256
from ..models.user import User, UserSession
from ..models.auth import AuthToken, LoginAttempt
from ..utils.rate_limiter import RateLimiter

class AuthenticationManager:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY')
        self.rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)
        self.session_manager = SessionManager()
        self.auth_logger = AuthLogger()
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str
    ) -> AuthToken:
        """Authenticate user and generate token"""
        try:
            # Check rate limiting
            await self.rate_limiter.check_rate_limit(ip_address)
            
            # Verify credentials
            user = await self._verify_credentials(username, password)
            if not user:
                await self._handle_failed_login(username, ip_address)
                raise AuthenticationError("Invalid credentials")
            
            # Create session
            session = await self.session_manager.create_session(
                user_id=user.id,
                ip_address=ip_address
            )
            
            # Generate token
            token = await self._generate_token(user, session.id)
            
            # Log successful login
            await self.auth_logger.log_login(
                user_id=user.id,
                ip_address=ip_address,
                success=True
            )
            
            return token
            
        except RateLimitExceeded:
            await self.auth_logger.log_rate_limit_exceeded(
                username=username,
                ip_address=ip_address
            )
            raise
    
    async def verify_token(self, token: str) -> User:
        """Verify JWT token and return user"""
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Verify session
            session = await self.session_manager.get_session(
                payload['session_id']
            )
            if not session or not session.is_active:
                raise AuthenticationError("Invalid session")
            
            # Get user
            user = await self._get_user(payload['user_id'])
            if not user:
                raise AuthenticationError("User not found")
            
            return user
            
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    async def _verify_credentials(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """Verify username and password"""
        user = await self._get_user_by_username(username)
        if not user:
            return None
            
        if not pbkdf2_sha256.verify(password, user.password_hash):
            return None
            
        return user
    
    async def _generate_token(
        self,
        user: User,
        session_id: str
    ) -> AuthToken:
        """Generate JWT token"""
        payload = {
            'user_id': user.id,
            'session_id': session_id,
            'roles': [role.name for role in user.roles],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )
        
        return AuthToken(
            access_token=token,
            token_type='bearer',
            expires_in=3600
        ) 