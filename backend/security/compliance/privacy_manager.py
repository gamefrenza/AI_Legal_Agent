from typing import Dict, Any, Set
import re
from ..models.compliance import PrivacyPolicy, PrivacyRule
from ..utils.pii_detector import PIIDetector

class PrivacyManager:
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.policy_validator = PrivacyPolicyValidator()
        self.rule_engine = PrivacyRuleEngine()
    
    async def identify_sensitive_data(
        self,
        content: str
    ) -> Dict[str, Any]:
        """Identify sensitive data in content"""
        sensitive_data = {}
        
        # Check for PII
        pii_data = await self.pii_detector.detect_pii(content)
        sensitive_data.update(pii_data)
        
        # Check for financial data
        financial_data = await self._detect_financial_data(content)
        sensitive_data.update(financial_data)
        
        # Check for legal identifiers
        legal_ids = await self._detect_legal_identifiers(content)
        sensitive_data.update(legal_ids)
        
        return sensitive_data
    
    async def apply_privacy_controls(
        self,
        content: str,
        sensitive_data: Dict[str, Any],
        policy: PrivacyPolicy
    ) -> str:
        """Apply privacy controls to content"""
        # Validate policy
        await self.policy_validator.validate_policy(policy)
        
        protected_content = content
        for field, value in sensitive_data.items():
            rule = await self.rule_engine.get_privacy_rule(field, policy)
            protected_content = await self._apply_privacy_rule(
                protected_content,
                value,
                rule
            )
        
        return protected_content
    
    async def _apply_privacy_rule(
        self,
        content: str,
        value: str,
        rule: PrivacyRule
    ) -> str:
        """Apply privacy rule to content"""
        if rule.action == 'mask':
            return self._mask_data(content, value, rule.mask_char)
        elif rule.action == 'encrypt':
            return await self._encrypt_data(content, value)
        elif rule.action == 'remove':
            return content.replace(value, '[REDACTED]')
        return content 