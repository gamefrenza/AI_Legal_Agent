import pytest
from unittest.mock import Mock, patch, AsyncMock
from ai_orchestrator.orchestrator import AIOrchestrator
from ai_orchestrator.agents import (
    ContractReviewAgent,
    ComplianceAgent,
    DocumentGenerationAgent,
    LegalResearchAgent,
    RiskAssessmentAgent
)
from ai_orchestrator.models.ai_config import AITask
from ai_orchestrator.utils.task_queue import TaskQueue
from ai_orchestrator.utils.result_aggregator import ResultAggregator

class TestAIOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        # Create mocks for dependencies
        with patch.object(AIOrchestrator, '_load_config', return_value={}):
            orchestrator = AIOrchestrator()
            
            # Replace agents with mocks
            orchestrator.agents = {
                'contract_review': AsyncMock(spec=ContractReviewAgent),
                'compliance': AsyncMock(spec=ComplianceAgent),
                'document_generation': AsyncMock(spec=DocumentGenerationAgent),
                'legal_research': AsyncMock(spec=LegalResearchAgent),
                'risk_assessment': AsyncMock(spec=RiskAssessmentAgent)
            }
            
            # Mock task queue and result aggregator
            orchestrator.task_queue = AsyncMock(spec=TaskQueue)
            orchestrator.result_aggregator = AsyncMock(spec=ResultAggregator)
            
            # Mock internal methods
            orchestrator._create_task = AsyncMock()
            orchestrator._update_task_status = AsyncMock()
            
            return orchestrator
    
    @pytest.mark.asyncio
    async def test_process_task(self, orchestrator):
        # Arrange
        task_data = {
            "type": "contract_review",
            "document_id": "doc123",
            "priority": "high",
            "context": {"jurisdiction": "US-CA"}
        }
        
        # Mock task creation
        task = AITask(id="task123", type="contract_review")
        orchestrator._create_task.return_value = task
        
        # Mock agent determination
        required_agents = ["contract_review", "risk_assessment"]
        orchestrator._determine_agents = AsyncMock(return_value=required_agents)
        
        # Mock subtask creation
        subtasks = [
            AITask(id="subtask1", type="contract_review"),
            AITask(id="subtask2", type="risk_assessment")
        ]
        orchestrator._create_subtasks = AsyncMock(return_value=subtasks)
        
        # Mock subtask execution
        subtask_results = [
            {"risk_level": "medium", "issues": ["clause 3.2 is ambiguous"]},
            {"risk_score": 65, "high_risk_areas": ["liability", "termination"]}
        ]
        orchestrator._execute_subtasks = AsyncMock(return_value=subtask_results)
        
        # Mock result aggregation
        final_result = {
            "risk_level": "medium",
            "risk_score": 65,
            "issues": ["clause 3.2 is ambiguous"],
            "high_risk_areas": ["liability", "termination"]
        }
        orchestrator.result_aggregator.aggregate.return_value = final_result
        
        # Act
        result = await orchestrator.process_task(task_data)
        
        # Assert
        assert result == final_result
        orchestrator._create_task.assert_called_once_with(task_data)
        orchestrator._determine_agents.assert_called_once_with(task)
        orchestrator._create_subtasks.assert_called_once_with(task, required_agents)
        orchestrator._execute_subtasks.assert_called_once_with(subtasks)
        orchestrator.result_aggregator.aggregate.assert_called_once_with(subtask_results)
        orchestrator._update_task_status.assert_called_once_with(task, final_result)
    
    @pytest.mark.asyncio
    async def test_determine_agents(self, orchestrator):
        # Restore original method for testing
        orchestrator._determine_agents = AIOrchestrator._determine_agents
        
        # Test cases for different task types
        test_cases = [
            {
                "task": AITask(id="task1", type="contract_review"),
                "expected_agents": ["contract_review", "risk_assessment"]
            },
            {
                "task": AITask(id="task2", type="document_generation"),
                "expected_agents": ["document_generation"]
            },
            {
                "task": AITask(id="task3", type="compliance_check"),
                "expected_agents": ["compliance"]
            },
            {
                "task": AITask(id="task4", type="legal_research"),
                "expected_agents": ["legal_research"]
            }
        ]
        
        for case in test_cases:
            # Act
            result = await orchestrator._determine_agents(case["task"])
            
            # Assert
            assert set(result) == set(case["expected_agents"])
    
    @pytest.mark.asyncio
    async def test_execute_subtasks(self, orchestrator):
        # Arrange
        subtasks = [
            AITask(id="subtask1", type="contract_review", agent="contract_review"),
            AITask(id="subtask2", type="risk_assessment", agent="risk_assessment")
        ]
        
        # Mock agent responses
        orchestrator.agents["contract_review"].process.return_value = {
            "issues": ["clause 3.2 is ambiguous"]
        }
        orchestrator.agents["risk_assessment"].process.return_value = {
            "risk_score": 65
        }
        
        # Restore original method for testing
        orchestrator._execute_subtasks = AIOrchestrator._execute_subtasks
        
        # Act
        results = await orchestrator._execute_subtasks(subtasks)
        
        # Assert
        assert len(results) == 2
        assert results[0]["issues"] == ["clause 3.2 is ambiguous"]
        assert results[1]["risk_score"] == 65
        orchestrator.agents["contract_review"].process.assert_called_once()
        orchestrator.agents["risk_assessment"].process.assert_called_once() 