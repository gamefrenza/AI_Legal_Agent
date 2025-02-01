from typing import Optional
from datetime import datetime, timedelta
from ..models.user import UserSession
from ..utils.ip_validator import IPValidator

class SessionManager:
    def __init__(self):
        self.session_store = SessionStore()
        self.ip_validator = IPValidator()
        self.max_sessions = 5
    
    async def create_session(
        self,
        user_id: str,
        ip_address: str
    ) -> UserSession:
        """Create new user session"""
        # Validate IP
        if not await self.ip_validator.is_valid(ip_address):
            raise SecurityError("Invalid IP address")
        
        # Check existing sessions
        await self._cleanup_expired_sessions(user_id)
        active_sessions = await self.get_active_sessions(user_id)
        if len(active_sessions) >= self.max_sessions:
            await self._terminate_oldest_session(user_id)
        
        # Create session
        session = UserSession(
            user_id=user_id,
            ip_address=ip_address,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            is_active=True
        )
        
        # Store session
        await self.session_store.store_session(session)
        
        return session
    
    async def validate_session(
        self,
        session_id: str,
        ip_address: str
    ) -> bool:
        """Validate session is active and from same IP"""
        session = await self.session_store.get_session(session_id)
        if not session:
            return False
            
        if not session.is_active:
            return False
            
        if session.ip_address != ip_address:
            await self._handle_ip_mismatch(session)
            return False
            
        if session.expires_at < datetime.utcnow():
            await self.terminate_session(session_id)
            return False
            
        return True 