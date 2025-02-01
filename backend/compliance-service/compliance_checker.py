from typing import Dict, List, Any, Optional
from datetime import datetime
from .rule_engine import RuleEngine
from .models.compliance import ComplianceCheck, ComplianceReport
from .utils.report_generator import ReportGenerator

class ComplianceChecker:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.report_generator = ReportGenerator()
    
    async def check_compliance(
        self,
        document: Dict[str, Any],
        jurisdiction: str,
        document_type: str,
        context: Optional[Dict] = None
    ) -> ComplianceCheck:
        """Check document compliance against rules"""
        
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
        
        # Generate report
        report = await self.report_generator.generate_report(check)
        
        # Store check and report
        await self._store_check(check)
        await self._store_report(report)
        
        return check
    
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