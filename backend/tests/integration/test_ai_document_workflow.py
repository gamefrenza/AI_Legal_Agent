import pytest
import json
from document_service.document_processor import DocumentProcessor
from ai_orchestrator.orchestrator import AIOrchestrator
from compliance_service.rule_engine import RuleEngine
from models.document import Document
from models.audit import AuditRecord

class TestAIDocumentWorkflow:
    @pytest.fixture
    async def workflow_components(self):
        document_processor = DocumentProcessor()
        ai_orchestrator = AIOrchestrator()
        rule_engine = RuleEngine()
        return document_processor, ai_orchestrator, rule_engine
    
    @pytest.mark.asyncio
    async def test_document_creation_with_ai_analysis(self, workflow_components):
        document_processor, ai_orchestrator, rule_engine = workflow_components
        
        # 1. Create a new document
        template_id = "employment-agreement"
        variables = {
            "employer_name": "Acme Corporation",
            "employee_name": "John Doe",
            "position": "Software Engineer",
            "start_date": "2024-04-01",
            "salary": "$120,000",
            "state": "California"
        }
        
        document = await document_processor.process_document(
            document_id=None,  # New document
            template_id=template_id,
            variables=variables,
            format="docx",
            user_id="user123",
            context={"jurisdiction": "US-CA"}
        )
        
        # Verify document was created
        assert document is not None
        assert document.id is not None
        
        # 2. Process document with AI
        ai_task_data = {
            "type": "contract_review",
            "document_id": document.id,
            "priority": "normal",
            "context": {
                "jurisdiction": "US-CA",
                "document_type": "employment_agreement"
            }
        }
        
        ai_analysis = await ai_orchestrator.process_task(ai_task_data)
        
        # Verify AI analysis
        assert ai_analysis is not None
        assert "risk_assessment" in ai_analysis
        assert "suggestions" in ai_analysis
        
        # 3. Check compliance
        compliance_results = await rule_engine.evaluate_rules(
            document={
                "id": document.id,
                "type": "employment_agreement",
                "content": document.content.decode("utf-8") if isinstance(document.content, bytes) else document.content
            },
            jurisdiction="US-CA",
            context={"document_type": "employment_agreement"}
        )
        
        # Verify compliance results
        assert compliance_results is not None
        assert isinstance(compliance_results, list)
    
    @pytest.mark.asyncio
    async def test_document_update_with_ai_feedback(self, workflow_components):
        document_processor, ai_orchestrator, rule_engine = workflow_components
        
        # 1. Create initial document
        document = await document_processor.process_document(
            document_id=None,
            template_id="nda-template",
            variables={"company": "Tech Corp", "recipient": "Partner Inc"},
            format="docx",
            user_id="user123",
            context={"jurisdiction": "US-NY"}
        )
        
        # 2. Get AI analysis
        ai_task_data = {
            "type": "contract_review",
            "document_id": document.id,
            "priority": "high",
            "context": {"jurisdiction": "US-NY", "document_type": "nda"}
        }
        
        ai_analysis = await ai_orchestrator.process_task(ai_task_data)
        
        # 3. Update document based on AI feedback
        updated_variables = {
            "company": "Tech Corp",
            "recipient": "Partner Inc",
            "term": "3 years",  # Added based on AI suggestion
            "governing_law": "New York"  # Added based on AI suggestion
        }
        
        updated_document = await document_processor.process_document(
            document_id=document.id,  # Update existing document
            template_id="nda-template",
            variables=updated_variables,
            format="docx",
            user_id="user123",
            context={"jurisdiction": "US-NY", "ai_suggestions": ai_analysis["suggestions"]}
        )
        
        # Verify document was updated
        assert updated_document is not None
        assert updated_document.id == document.id
        assert updated_document.version > document.version
        
        # 4. Re-analyze with AI
        ai_task_data["document_id"] = updated_document.id
        updated_ai_analysis = await ai_orchestrator.process_task(ai_task_data)
        
        # Verify improved analysis results
        assert updated_ai_analysis["risk_assessment"]["score"] < ai_analysis["risk_assessment"]["score"]
        
        # 5. Check compliance again
        updated_compliance_results = await rule_engine.evaluate_rules(
            document={
                "id": updated_document.id,
                "type": "nda",
                "content": updated_document.content.decode("utf-8") if isinstance(updated_document.content, bytes) else updated_document.content
            },
            jurisdiction="US-NY",
            context={"document_type": "nda"}
        )
        
        # Verify improved compliance
        assert len([r for r in updated_compliance_results if r.get("result") == "flagged"]) < len([r for r in ai_analysis.get("compliance_issues", []) if r.get("status") == "flagged"])
    
    @pytest.mark.asyncio
    async def test_multi_jurisdiction_compliance(self, workflow_components):
        document_processor, ai_orchestrator, rule_engine = workflow_components
        
        # 1. Create a document
        document = await document_processor.process_document(
            document_id=None,
            template_id="privacy-policy",
            variables={"company_name": "Global Tech", "website": "globaltech.com"},
            format="docx",
            user_id="user123",
            context={"jurisdiction": "multi"}
        )
        
        # 2. Check compliance across multiple jurisdictions
        jurisdictions = ["US-CA", "EU-GDPR", "UK"]
        compliance_by_jurisdiction = {}
        
        for jurisdiction in jurisdictions:
            results = await rule_engine.evaluate_rules(
                document={
                    "id": document.id,
                    "type": "privacy_policy",
                    "content": document.content.decode("utf-8") if isinstance(document.content, bytes) else document.content
                },
                jurisdiction=jurisdiction,
                context={"document_type": "privacy_policy"}
            )
            compliance_by_jurisdiction[jurisdiction] = results
        
        # 3. Process with AI to get suggestions for all jurisdictions
        ai_task_data = {
            "type": "compliance_check",
            "document_id": document.id,
            "priority": "high",
            "context": {
                "jurisdictions": jurisdictions,
                "document_type": "privacy_policy",
                "compliance_results": compliance_by_jurisdiction
            }
        }
        
        ai_analysis = await ai_orchestrator.process_task(ai_task_data)
        
        # Verify AI provided suggestions for each jurisdiction
        assert "jurisdiction_specific_suggestions" in ai_analysis
        assert len(ai_analysis["jurisdiction_specific_suggestions"]) == len(jurisdictions)
        
        # 4. Update document with AI suggestions
        updated_document = await document_processor.process_document(
            document_id=document.id,
            template_id="privacy-policy",
            variables={
                "company_name": "Global Tech",
                "website": "globaltech.com",
                "gdpr_clause": ai_analysis["jurisdiction_specific_suggestions"]["EU-GDPR"]["recommended_text"],
                "ccpa_clause": ai_analysis["jurisdiction_specific_suggestions"]["US-CA"]["recommended_text"]
            },
            format="docx",
            user_id="user123",
            context={"jurisdiction": "multi"}
        )
        
        # 5. Verify improved compliance
        improved_compliance = {}
        for jurisdiction in jurisdictions:
            results = await rule_engine.evaluate_rules(
                document={
                    "id": updated_document.id,
                    "type": "privacy_policy",
                    "content": updated_document.content.decode("utf-8") if isinstance(updated_document.content, bytes) else updated_document.content
                },
                jurisdiction=jurisdiction,
                context={"document_type": "privacy_policy"}
            )
            improved_compliance[jurisdiction] = results
            
            # Should have fewer flags than before
            original_flags = len([r for r in compliance_by_jurisdiction[jurisdiction] if r.get("result") == "flagged"])
            new_flags = len([r for r in results if r.get("result") == "flagged"])
            assert new_flags < original_flags 