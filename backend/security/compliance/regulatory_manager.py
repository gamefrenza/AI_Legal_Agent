from typing import Dict, Any, List
from datetime import datetime
from ..models.compliance import (
    Regulation,
    ComplianceRequirement,
    ComplianceStatus
)

class RegulatoryComplianceManager:
    def __init__(self):
        self.regulation_store = RegulationStore()
        self.requirement_validator = RequirementValidator()
        self.compliance_checker = ComplianceChecker()
    
    async def check_regulatory_compliance(
        self,
        document: Document,
        regulations: List[str]
    ) -> ComplianceStatus:
        """Check document compliance with regulations"""
        compliance_status = ComplianceStatus(
            document_id=document.id,
            timestamp=datetime.utcnow(),
            results={}
        )
        
        for reg_code in regulations:
            # Get regulation requirements
            regulation = await self.regulation_store.get_regulation(reg_code)
            
            # Check each requirement
            reg_results = []
            for requirement in regulation.requirements:
                result = await self.compliance_checker.check_requirement(
                    document,
                    requirement
                )
                reg_results.append(result)
            
            # Aggregate results
            compliance_status.results[reg_code] = {
                'compliant': all(r.compliant for r in reg_results),
                'requirements': reg_results,
                'timestamp': datetime.utcnow()
            }
        
        return compliance_status
    
    async def generate_compliance_report(
        self,
        compliance_status: ComplianceStatus
    ) -> Dict[str, Any]:
        """Generate detailed compliance report"""
        report = {
            'document_id': compliance_status.document_id,
            'timestamp': datetime.utcnow(),
            'overall_status': all(
                r['compliant'] 
                for r in compliance_status.results.values()
            ),
            'regulations': {}
        }
        
        for reg_code, results in compliance_status.results.items():
            regulation = await self.regulation_store.get_regulation(reg_code)
            report['regulations'][reg_code] = {
                'name': regulation.name,
                'status': results['compliant'],
                'requirements': [
                    {
                        'id': req.id,
                        'description': req.description,
                        'status': req.compliant,
                        'details': req.details
                    }
                    for req in results['requirements']
                ],
                'timestamp': results['timestamp']
            }
        
        return report 