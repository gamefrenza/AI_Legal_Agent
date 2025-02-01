import pytest
from compliance_service.rule_engine import ComplianceRuleEngine
from compliance_service.models import ComplianceRule, ComplianceResult

class TestComplianceEngine:
    @pytest.fixture
    def rule_engine(self):
        return ComplianceRuleEngine()
    
    @pytest.mark.asyncio
    async def test_evaluate_document(self, rule_engine):
        # Arrange
        document = {
            "type": "contract",
            "content": "Test contract content",
            "jurisdiction": "US-CA"
        }
        
        # Act
        results = await rule_engine.evaluate_document(
            document=document,
            jurisdiction="US-CA"
        )
        
        # Assert
        assert isinstance(results, list)
        assert all(isinstance(r, ComplianceResult) for r in results)
    
    @pytest.mark.asyncio
    async def test_rule_validation(self, rule_engine):
        # Arrange
        invalid_rule = ComplianceRule(
            id="test-rule",
            conditions="invalid condition",
            actions=[]
        )
        
        # Act & Assert
        with pytest.raises(ValueError):
            await rule_engine.validate_rule(invalid_rule) 