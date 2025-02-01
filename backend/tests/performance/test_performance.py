import pytest
import asyncio
import time
from document_service.document_engine import DocumentEngine
from compliance_service.rule_engine import ComplianceRuleEngine

class TestPerformance:
    @pytest.fixture
    async def performance_components(self):
        document_engine = DocumentEngine()
        compliance_engine = ComplianceRuleEngine()
        return document_engine, compliance_engine
    
    @pytest.mark.asyncio
    async def test_document_generation_performance(self, performance_components):
        document_engine, _ = performance_components
        
        # Measure document generation time
        start_time = time.time()
        
        # Generate multiple documents concurrently
        tasks = []
        for _ in range(10):
            task = document_engine.generate_document(
                template_id="test-template",
                variables={"test": "data"}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Assert performance metrics
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert len(results) == 10
    
    @pytest.mark.asyncio
    async def test_compliance_check_performance(self, performance_components):
        _, compliance_engine = performance_components
        
        # Test document
        document = {
            "content": "Test content",
            "jurisdiction": "US-CA"
        }
        
        # Measure compliance check time
        start_time = time.time()
        result = await compliance_engine.check_compliance(
            document,
            context={"jurisdiction": "US-CA"}
        )
        end_time = time.time()
        
        # Assert performance
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should complete within 1 second 