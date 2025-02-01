from typing import Dict, Any, Optional, List
from datetime import datetime
from ..models.audit import ActivityLog
from ..utils.anomaly_detector import AnomalyDetector

class ActivityMonitor:
    def __init__(self):
        self.activity_store = ActivityStore()
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()
    
    async def log_activity(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Log user activity"""
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        
        # Store activity
        await self.activity_store.store_activity(activity)
        
        # Check for anomalies
        if await self.anomaly_detector.check_activity(activity):
            await self._handle_anomaly(activity)
    
    async def get_user_activity(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ActivityLog]:
        """Get user activity history"""
        return await self.activity_store.get_user_activities(
            user_id,
            start_time,
            end_time
        )
    
    async def _handle_anomaly(self, activity: ActivityLog) -> None:
        """Handle detected anomalous activity"""
        # Log security event
        await self.alert_manager.create_alert(
            level='WARNING',
            type='ANOMALOUS_ACTIVITY',
            details={
                'activity_id': activity.id,
                'user_id': activity.user_id,
                'action': activity.action,
                'timestamp': activity.timestamp
            }
        ) 