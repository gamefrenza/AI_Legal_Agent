from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import os
import logging
from .rule_engine import RuleEngine
from .models.compliance import ComplianceCheck, ComplianceReport
from .utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class ComplianceChecker:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.report_generator = ReportGenerator()
        self.notification_service_url = os.getenv(
            'NOTIFICATION_SERVICE_URL',
            'http://notification-service:8000'
        )
    
    async def check_compliance(
        self,
        document: Dict[str, Any],
        jurisdiction: str,
        document_type: str,
        user_id: str,
        context: Optional[Dict] = None
    ) -> ComplianceCheck:
        """Check document compliance against rules"""
        try:
            # Evaluate rules
            rule_results = await self.rule_engine.evaluate_rules(
                document,
                jurisdiction,
                context
            )
            
            # Create compliance check record
            check = ComplianceCheck(
                document_id=document['id'],
                jurisdiction=jurisdiction,
                document_type=document_type,
                timestamp=datetime.utcnow(),
                results=rule_results,
                is_compliant=all(r['status'] == 'compliant' for r in rule_results),
                context=context
            )
            
            # If there are compliance issues, send notifications
            if not check.is_compliant:
                try:
                    await self._send_compliance_notifications(check, user_id)
                except Exception as e:
                    logger.error(f"Error sending compliance notifications: {str(e)}")
                    # Don't block the compliance check if notifications fail
            
            # Generate report
            report = await self.report_generator.generate_report(check)
            
            # Store check and report
            await self._store_check(check)
            await self._store_report(report)
            
            return check
        except Exception as e:
            logger.error(f"Error in compliance check: {str(e)}")
            raise
    
    async def _send_compliance_notifications(self, check: ComplianceCheck, user_id: str):
        """Send notifications for compliance issues"""
        violations = [r for r in check.results if r['status'] != 'compliant']
        
        # Group violations by severity
        severity_groups = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for violation in violations:
            severity = self._determine_violation_severity(violation)
            severity_groups[severity].append(violation)
        
        # Send notifications for each severity group
        async with httpx.AsyncClient() as client:
            for severity, violations in severity_groups.items():
                if violations:
                    notification_data = {
                        "user_id": user_id,
                        "type": "compliance_issue",
                        "severity": severity,
                        "message": f"Found {len(violations)} {severity} compliance issues in document {check.document_id}",
                        "details": {
                            "document_id": check.document_id,
                            "jurisdiction": check.jurisdiction,
                            "violations": violations,
                            "timestamp": check.timestamp.isoformat()
                        }
                    }
                    
                    try:
                        await client.post(
                            f"{self.notification_service_url}/notifications/send",
                            json=notification_data
                        )
                    except Exception as e:
                        # Log error but don't block the compliance check
                        print(f"Error sending notification: {str(e)}")
    
    def _determine_violation_severity(self, violation: Dict[str, Any]) -> str:
        """Determine the severity of a compliance violation"""
        # Implement severity determination logic based on:
        # - Rule importance
        # - Potential impact
        # - Legal requirements
        # - Industry standards
        
        if violation.get('rule_type') == 'critical' or violation.get('impact') == 'severe':
            return 'critical'
        elif violation.get('rule_type') == 'major' or violation.get('impact') == 'high':
            return 'high'
        elif violation.get('rule_type') == 'standard' or violation.get('impact') == 'medium':
            return 'medium'
        else:
            return 'low'
    
    async def get_compliance_status(
        self,
        document_id: str,
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Get current compliance status for document"""
        
        # Get latest compliance check
        check = await self._get_latest_check(document_id, jurisdiction)
        
        # Get applicable regulations
        regulations = await self._get_applicable_regulations(jurisdiction)
        
        return {
            'is_compliant': check.is_compliant,
            'last_check': check.timestamp,
            'violations': [r for r in check.results if r['status'] == 'violation'],
            'regulations': regulations
        } 