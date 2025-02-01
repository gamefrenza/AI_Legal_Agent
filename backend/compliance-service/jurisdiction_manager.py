from typing import Dict, List, Any, Optional
from datetime import datetime
from .models.compliance import Jurisdiction, JurisdictionRule
from .utils.rule_validator import RuleValidator

class JurisdictionManager:
    def __init__(self):
        self.rule_validator = RuleValidator()
        self.jurisdictions = {}
        
    async def add_jurisdiction(
        self,
        jurisdiction: Jurisdiction
    ) -> None:
        """Add new jurisdiction with rules"""
        
        # Validate jurisdiction rules
        valid = await self.rule_validator.validate_rules(
            jurisdiction.rules
        )
        
        if not valid:
            raise ValueError("Invalid jurisdiction rules")
        
        # Add to managed jurisdictions
        self.jurisdictions[jurisdiction.code] = jurisdiction
        
        # Initialize rule sets
        await self._initialize_rule_sets(jurisdiction)
    
    async def get_applicable_rules(
        self,
        jurisdiction_code: str,
        document_type: str,
        context: Optional[Dict] = None
    ) -> List[JurisdictionRule]:
        """Get applicable rules for jurisdiction and document type"""
        
        jurisdiction = self.jurisdictions.get(jurisdiction_code)
        if not jurisdiction:
            raise ValueError(f"Unknown jurisdiction: {jurisdiction_code}")
        
        # Filter rules by document type and context
        rules = []
        for rule in jurisdiction.rules:
            if await self._is_rule_applicable(rule, document_type, context):
                rules.append(rule)
        
        return rules
    
    async def update_jurisdiction_rules(
        self,
        jurisdiction_code: str,
        updates: List[Dict[str, Any]]
    ) -> None:
        """Update jurisdiction rules"""
        
        jurisdiction = self.jurisdictions.get(jurisdiction_code)
        if not jurisdiction:
            raise ValueError(f"Unknown jurisdiction: {jurisdiction_code}")
        
        # Validate updates
        valid = await self.rule_validator.validate_updates(updates)
        if not valid:
            raise ValueError("Invalid rule updates")
        
        # Apply updates
        await self._apply_rule_updates(jurisdiction, updates)
        
        # Notify affected parties
        await self._notify_rule_changes(jurisdiction_code, updates) 