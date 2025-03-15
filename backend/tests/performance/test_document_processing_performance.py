import pytest
import asyncio
import time
from datetime import datetime
from document_service.document_processor import DocumentProcessor
from ai_orchestrator.orchestrator import AIOrchestrator
from compliance_service.rule_engine import RuleEngine

class TestDocumentProcessingPerformance:
    @pytest.fixture
    async def performance_components(self):
        document_processor = DocumentProcessor()
        ai_orchestrator = AIOrchestrator()
        rule_engine = RuleEngine()
        return document_processor, ai_orchestrator, rule_engine
    
    @pytest.mark.asyncio
    async def test_document_generation_throughput(self, performance_components):
        document_processor, _, _ = performance_components
        
        # Test parameters
        num_documents = 10
        template_id = "simple-agreement"
        
        # Prepare variables for each document
        document_variables = [
            {
                "company_name": f"Company {i}",
                "client_name": f"Client {i}",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            for i in range(num_documents)
        ]
        
        # Measure time to generate documents
        start_time = time.time()
        
        # Create tasks for concurrent document generation
        tasks = [
            document_processor.process_document(
                document_id=None,
                template_id=template_id,
                variables=variables,
                format="docx",
                user_id="performance-test",
                context={"test_type": "performance"}
            )
            for variables in document_variables
        ]
        
        # Execute tasks concurrently
        documents = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate throughput
        throughput = num_documents / total_time
        
        # Log performance metrics
        print(f"Generated {num_documents} documents in {total_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} documents per second")
        
        # Verify all documents were created successfully
        assert len(documents) == num_documents
        assert all(doc is not None for doc in documents)
        
        # Performance assertion - should generate at least 1 document per second
        assert throughput >= 1.0, f"Document generation throughput too low: {throughput:.2f} docs/sec"
    
    @pytest.mark.asyncio
    async def test_ai_processing_performance(self, performance_components):
        _, ai_orchestrator, _ = performance_components
        
        # Test parameters
        num_tasks = 5
        
        # Prepare AI tasks
        ai_tasks = [
            {
                "type": "contract_review",
                "document_id": f"perf-doc-{i}",
                "priority": "normal",
                "context": {
                    "jurisdiction": "US-CA",
                    "document_type": "contract"
                }
            }
            for i in range(num_tasks)
        ]
        
        # Measure time for AI processing
        start_time = time.time()
        
        # Create tasks for concurrent AI processing
        tasks = [
            ai_orchestrator.process_task(task_data)
            for task_data in ai_tasks
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate average processing time
        avg_time_per_task = total_time / num_tasks
        
        # Log performance metrics
        print(f"Processed {num_tasks} AI tasks in {total_time:.2f} seconds")
        print(f"Average time per task: {avg_time_per_task:.2f} seconds")
        
        # Verify all tasks completed successfully
        assert len(results) == num_tasks
        assert all(result is not None for result in results)
        
        # Performance assertion - each AI task should complete in reasonable time
        assert avg_time_per_task <= 5.0, f"AI processing too slow: {avg_time_per_task:.2f} sec/task"
    
    @pytest.mark.asyncio
    async def test_compliance_check_performance(self, performance_components):
        _, _, rule_engine = performance_components
        
        # Test parameters
        num_checks = 20
        jurisdictions = ["US-CA", "US-NY", "EU-GDPR", "UK"]
        document_types = ["contract", "privacy_policy", "terms_of_service"]
        
        # Generate test documents
        test_documents = [
            {
                "id": f"perf-doc-{i}",
                "type": document_types[i % len(document_types)],
                "content": f"This is a test document {i} with some content for performance testing."
            }
            for i in range(num_checks)
        ]
        
        # Measure time for compliance checks
        start_time = time.time()
        
        # Create tasks for concurrent compliance checks
        tasks = [
            rule_engine.evaluate_rules(
                document=doc,
                jurisdiction=jurisdictions[i % len(jurisdictions)],
                context={"document_type": doc["type"]}
            )
            for i, doc in enumerate(test_documents)
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate throughput
        throughput = num_checks / total_time
        
        # Log performance metrics
        print(f"Performed {num_checks} compliance checks in {total_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} checks per second")
        
        # Verify all checks completed successfully
        assert len(results) == num_checks
        assert all(result is not None for result in results)
        
        # Performance assertion - should process at least 2 compliance checks per second
        assert throughput >= 2.0, f"Compliance check throughput too low: {throughput:.2f} checks/sec"
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow_performance(self, performance_components):
        document_processor, ai_orchestrator, rule_engine = performance_components
        
        # Test parameters
        num_workflows = 3
        
        # Measure time for end-to-end workflows
        start_time = time.time()
        
        # Execute complete workflows sequentially (as they depend on each other)
        for i in range(num_workflows):
            # 1. Create document
            document = await document_processor.process_document(
                document_id=None,
                template_id="contract-template",
                variables={
                    "company_name": f"Company {i}",
                    "client_name": f"Client {i}"
                },
                format="docx",
                user_id="performance-test",
                context={"jurisdiction": "US-CA"}
            )
            
            # 2. Process with AI
            ai_result = await ai_orchestrator.process_task({
                "type": "contract_review",
                "document_id": document.id,
                "priority": "high",
                "context": {
                    "jurisdiction": "US-CA",
                    "document_type": "contract"
                }
            })
            
            # 3. Check compliance
            compliance_result = await rule_engine.evaluate_rules(
                document={
                    "id": document.id,
                    "type": "contract",
                    "content": document.content.decode("utf-8") if isinstance(document.content, bytes) else document.content
                },
                jurisdiction="US-CA",
                context={"document_type": "contract"}
            )
            
            # 4. Update document based on AI and compliance results
            updated_document = await document_processor.process_document(
                document_id=document.id,
                template_id="contract-template",
                variables={
                    "company_name": f"Company {i}",
                    "client_name": f"Client {i}",
                    "additional_clause": ai_result.get("suggestions", [{}])[0].get("text", "")
                },
                format="docx",
                user_id="performance-test",
                context={"jurisdiction": "US-CA"}
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate average workflow time
        avg_time_per_workflow = total_time / num_workflows
        
        # Log performance metrics
        print(f"Completed {num_workflows} end-to-end workflows in {total_time:.2f} seconds")
        print(f"Average time per workflow: {avg_time_per_workflow:.2f} seconds")
        
        # Performance assertion - each workflow should complete in reasonable time
        assert avg_time_per_workflow <= 15.0, f"End-to-end workflow too slow: {avg_time_per_workflow:.2f} sec/workflow" 