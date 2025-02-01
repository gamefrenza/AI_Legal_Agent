from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import aiohttp
from ..models.integration import IntegrationStatus, SyncLog
from ..utils.security import SecurityManager
from ..utils.rate_limiter import RateLimiter

class BaseIntegration(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_manager = SecurityManager()
        self.rate_limiter = RateLimiter(
            max_requests=config.get('rate_limit', 100),
            time_window=60
        )
        self.status_tracker = StatusTracker()
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external system"""
        pass
    
    @abstractmethod
    async def sync_data(self) -> SyncLog:
        """Synchronize data with external system"""
        pass
    
    async def execute_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute authenticated request to external system"""
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Prepare request
            auth_headers = await self.security_manager.get_auth_headers(
                self.config['credentials']
            )
            headers = {**(headers or {}), **auth_headers}
            
            # Execute request
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    f"{self.config['base_url']}{endpoint}",
                    json=data,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except Exception as e:
            await self.handle_error(e)
            raise
    
    async def handle_error(self, error: Exception) -> None:
        """Handle integration errors"""
        await self.status_tracker.log_error(
            integration_id=self.config['integration_id'],
            error=error
        )
        # Additional error handling logic 