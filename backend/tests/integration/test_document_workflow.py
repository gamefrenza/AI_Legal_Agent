import pytest
from document_service.document_engine import DocumentEngine
from compliance_service.rule_engine import ComplianceRuleEngine
from ai_orchestrator.orchestrator import AIOrchestrator

class TestDocumentWorkflow:
    @pytest.fixture
    async def workflow_components(self):
        document_engine = DocumentEngine()
        compliance_engine = ComplianceRuleEngine()
        ai_orchestrator = AIOrchestrator()
        return document_engine, compliance_engine, ai_orchestrator
    
    @pytest.mark.asyncio
    async def test_complete_document_workflow(self, workflow_components):
        document_engine, compliance_engine, ai_orchestrator = workflow_components
        
        # 1. Generate document
        document = await document_engine.generate_document(
            template_id="contract-template",
            variables={"client": "Test Corp"}
        )
        
        # 2. AI Review
        ai_review = await ai_orchestrator.process_document(document)
        
        # 3. Compliance Check
        compliance_results = await compliance_engine.check_compliance(
            document,
            context={"jurisdiction": "US-CA"}
        )
        
        # Assertions
        assert document is not None
        assert ai_review['risks'] is not None
        assert compliance_results.is_compliant is True 