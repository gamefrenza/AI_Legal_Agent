import pytest
from compliance_service.rule_engine import RuleEngine
from compliance_service.jurisdiction_manager import JurisdictionManager
from compliance_service.regulatory_tracker import RegulatoryTracker
from document_service.document_processor import DocumentProcessor
from models.document import Document
from models.compliance import ComplianceResult, ComplianceRule

class TestRegulatoryCompliance:
    @pytest.fixture
    async def compliance_components(self):
        rule_engine = RuleEngine()
        jurisdiction_manager = JurisdictionManager()
        regulatory_tracker = RegulatoryTracker()
        document_processor = DocumentProcessor()
        return rule_engine, jurisdiction_manager, regulatory_tracker, document_processor
    
    @pytest.mark.asyncio
    async def test_gdpr_compliance(self, compliance_components):
        rule_engine, jurisdiction_manager, regulatory_tracker, document_processor = compliance_components
        
        # 1. Create a privacy policy document
        document = await document_processor.process_document(
            document_id=None,
            template_id="privacy-policy",
            variables={"company_name": "Example Corp"},
            format="docx",
            user_id="user123",
            context={"jurisdiction": "EU-GDPR"}
        )
        
        # 2. Get GDPR rules
        gdpr_rules = await jurisdiction_manager.get_rules_for_jurisdiction(
            jurisdiction="EU-GDPR",
            document_type="privacy_policy"
        )
        
        # Verify essential GDPR rules exist
        required_gdpr_topics = [
            "data_subject_rights",
            "data_processing_purpose",
            "data_retention",
            "data_transfer",
            "consent"
        ]
        
        for topic in required_gdpr_topics:
            matching_rules = [rule for rule in gdpr_rules if topic in rule.tags]
            assert len(matching_rules) > 0, f"No rules found for GDPR topic: {topic}"
        
        # 3. Check document compliance
        compliance_results = await rule_engine.evaluate_rules(
            document={
                "id": document.id,
                "type": "privacy_policy",
                "content": document.content.decode("utf-8") if isinstance(document.content, bytes) else document.content
            },
            jurisdiction="EU-GDPR",
            context={"document_type": "privacy_policy"}
        )
        
        # 4. Analyze compliance gaps
        compliance_gaps = [
            result for result in compliance_results 
            if result.get("result") == "flagged"
        ]
        
        # Document the compliance gaps
        for gap in compliance_gaps:
            print(f"GDPR Compliance Gap: {gap.get('message')}")
            
        # 5. Verify regulatory updates are tracked
        recent_updates = await regulatory_tracker.get_recent_updates(
            jurisdiction="EU-GDPR",
            days=90
        )
        
        # Check if any recent updates affect our document
        affected_by_updates = await regulatory_tracker.check_document_affected(
            document_id=document.id,
            updates=recent_updates
        )
        
        # Document should indicate if affected by recent regulatory changes
        if affected_by_updates:
            print(f"Document affected by {len(affected_by_updates)} recent regulatory changes")
    
    @pytest.mark.asyncio
    async def test_ccpa_compliance(self, compliance_components):
        rule_engine, jurisdiction_manager, regulatory_tracker, document_processor = compliance_components
        
        # 1. Create a privacy policy for California
        document = await document_processor.process_document(
            document_id=None,
            template_id="privacy-policy",
            variables={"company_name": "Example Corp", "state": "California"},
            format="docx",
            user_id="user123",
            context={"jurisdiction": "US-CA"}
        )
        
        # 2. Get CCPA rules
        ccpa_rules = await jurisdiction_manager.get_rules_for_jurisdiction(
            jurisdiction="US-CA",
            document_type="privacy_policy"
        )
        
        # Verify essential CCPA rules exist
        required_ccpa_topics = [
            "right_to_delete",
            "right_to_know",
            "right_to_opt_out",
            "non_discrimination",
            "notice_at_collection"
        ]
        
        for topic in required_ccpa_topics:
            matching_rules = [rule for rule in ccpa_rules if topic in rule.tags]
            assert len(matching_rules) > 0, f"No rules found for CCPA topic: {topic}"
        
        # 3. Check document compliance
        compliance_results = await rule_engine.evaluate_rules(
            document={
                "id": document.id,
                "type": "privacy_policy",
                "content": document.content.decode("utf-8") if isinstance(document.content, bytes) else document.content
            },
            jurisdiction="US-CA",
            context={"document_type": "privacy_policy"}
        )
        
        # 4. Analyze compliance gaps
        compliance_gaps = [
            result for result in compliance_results 
            if result.get("result") == "flagged"
        ]
        
        # Document the compliance gaps
        for gap in compliance_gaps:
            print(f"CCPA Compliance Gap: {gap.get('message')}")
    
    @pytest.mark.asyncio
    async def test_employment_law_compliance(self, compliance_components):
        rule_engine, jurisdiction_manager, regulatory_tracker, document_processor = compliance_components
        
        # Test employment agreements across different jurisdictions
        jurisdictions = ["US-CA", "US-NY", "UK"]
        
        for jurisdiction in jurisdictions:
            # 1. Create an employment agreement
            document = await document_processor.process_document(
                document_id=None,
                template_id="employment-agreement",
                variables={
                    "employer_name": "Example Corp",
                    "employee_name": "John Doe",
                    "position": "Software Engineer",
                    "jurisdiction": jurisdiction
                },
                format="docx",
                user_id="user123",
                context={"jurisdiction": jurisdiction}
            )
            
            # 2. Check document compliance
            compliance_results = await rule_engine.evaluate_rules(
                document={
                    "id": document.id,
                    "type": "employment_agreement",
                    "content": document.content.decode("utf-8") if isinstance(document.content, bytes) else document.content
                },
                jurisdiction=jurisdiction,
                context={"document_type": "employment_agreement"}
            )
            
            # 3. Verify jurisdiction-specific rules were applied
            jurisdiction_specific_results = [
                result for result in compliance_results
                if result.get("jurisdiction_specific") is True
            ]
            
            # Each jurisdiction should have specific employment law requirements
            assert len(jurisdiction_specific_results) > 0, f"No jurisdiction-specific rules applied for {jurisdiction}"
            
            # 4. Analyze compliance gaps
            compliance_gaps = [
                result for result in compliance_results 
                if result.get("result") == "flagged"
            ]
            
            # Document the compliance gaps
            for gap in compliance_gaps:
                print(f"{jurisdiction} Employment Law Compliance Gap: {gap.get('message')}")
    
    @pytest.mark.asyncio
    async def test_regulatory_change_impact(self, compliance_components):
        rule_engine, jurisdiction_manager, regulatory_tracker, document_processor = compliance_components
        
        # 1. Create a document
        document = await document_processor.process_document(
            document_id=None,
            template_id="terms-of-service",
            variables={"company_name": "Example Corp"},
            format="docx",
            user_id="user123",
            context={"jurisdiction": "multi"}
        )
        
        # 2. Simulate a regulatory change
        new_regulation = {
            "id": "reg-2024-01",
            "name": "New Data Protection Regulation",
            "jurisdiction": "EU-GDPR",
            "effective_date": "2024-06-01",
            "description": "Enhanced requirements for data processing disclosures",
            "affected_document_types": ["terms_of_service", "privacy_policy"],
            "required_clauses": ["enhanced_disclosure"]
        }
        
        await regulatory_tracker.add_regulatory_update(new_regulation)
        
        # 3. Check if document is affected by the change
        affected_documents = await regulatory_tracker.find_affected_documents(
            regulation_id=new_regulation["id"]
        )
        
        # Our document should be in the affected list
        assert document.id in [doc.id for doc in affected_documents]
        
        # 4. Get compliance recommendations for the regulatory change
        recommendations = await regulatory_tracker.get_compliance_recommendations(
            document_id=document.id,
            regulation_id=new_regulation["id"]
        )
        
        # Verify recommendations include required clauses
        assert any("enhanced_disclosure" in rec.get("action", "") for rec in recommendations)
        
        # 5. Apply recommendations to document
        updated_variables = {
            "company_name": "Example Corp",
            "enhanced_disclosure": recommendations[0].get("suggested_text", "")
        }
        
        updated_document = await document_processor.process_document(
            document_id=document.id,
            template_id="terms-of-service",
            variables=updated_variables,
            format="docx",
            user_id="user123",
            context={"jurisdiction": "multi"}
        )
        
        # 6. Verify compliance after update
        compliance_results = await rule_engine.evaluate_rules(
            document={
                "id": updated_document.id,
                "type": "terms_of_service",
                "content": updated_document.content.decode("utf-8") if isinstance(updated_document.content, bytes) else updated_document.content
            },
            jurisdiction="EU-GDPR",
            context={"document_type": "terms_of_service"}
        )
        
        # Check if the specific regulation is now complied with
        regulation_compliance = next(
            (result for result in compliance_results if result.get("regulation_id") == new_regulation["id"]),
            None
        )
        
        assert regulation_compliance is not None
        assert regulation_compliance.get("result") == "passed" 