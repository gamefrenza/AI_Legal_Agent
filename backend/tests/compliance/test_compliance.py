import pytest
from compliance_service.rule_engine import ComplianceRuleEngine
from compliance_service.models import ComplianceRule, Regulation

class TestCompliance:
    @pytest.fixture
    def compliance_engine(self):
        return ComplianceRuleEngine()
    
    @pytest.mark.asyncio
    async def test_gdpr_compliance(self, compliance_engine):
        # Test document with personal data
        document = {
            "content": "Personal data: John Doe, john@email.com",
            "jurisdiction": "EU"
        }
        
        # Check GDPR compliance
        results = await compliance_engine.check_compliance(
            document,
            context={"regulation": "GDPR"}
        )
        
        # Assert GDPR requirements
        assert results.has_personal_data == True
        assert results.requires_consent == True
        assert results.data_protection_measures is not None
    
    @pytest.mark.asyncio
    async def test_hipaa_compliance(self, compliance_engine):
        # Test medical document
        document = {
            "content": "Medical record content",
            "jurisdiction": "US",
            "document_type": "medical"
        }
        
        # Check HIPAA compliance
        results = await compliance_engine.check_compliance(
            document,
            context={"regulation": "HIPAA"}
        )
        
        # Assert HIPAA requirements
        assert results.contains_phi == True
        assert results.security_measures_adequate == True
        assert results.requires_authorization == True
    
    @pytest.mark.asyncio
    async def test_multi_jurisdiction_compliance(self, compliance_engine):
        # Test document subject to multiple jurisdictions
        document = {
            "content": "International contract content",
            "jurisdictions": ["US", "EU", "UK"]
        }
        
        # Check compliance for all jurisdictions
        results = await compliance_engine.check_multi_jurisdiction_compliance(
            document,
            jurisdictions=document["jurisdictions"]
        )
        
        # Assert compliance for each jurisdiction
        for jurisdiction in document["jurisdictions"]:
            assert results[jurisdiction].is_compliant is not None
            assert results[jurisdiction].applicable_regulations is not None 