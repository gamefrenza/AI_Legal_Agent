import pytest
from unittest.mock import Mock, patch, AsyncMock
from compliance_service.rule_engine import RuleEngine
from compliance_service.models.compliance import ComplianceRule, RuleCondition, RuleAction
from compliance_service.utils.rule_parser import RuleParser

class TestRuleEngine:
    @pytest.fixture
    def rule_engine(self):
        # Create mocks for dependencies
        rule_engine = RuleEngine()
        rule_engine.rule_parser = Mock(spec=RuleParser)
        
        # Mock internal methods
        rule_engine._get_applicable_rules = AsyncMock()
        
        return rule_engine
    
    @pytest.mark.asyncio
    async def test_evaluate_rules(self, rule_engine):
        # Arrange
        document = {
            "id": "doc123",
            "type": "contract",
            "content": "Sample contract content"
        }
        jurisdiction = "US-CA"
        context = {"client_type": "corporate"}
        
        # Mock applicable rules
        rules = [
            ComplianceRule(
                id="rule1",
                name="California Privacy Rule",
                conditions=[{"field": "content", "operator": "contains", "value": "privacy"}],
                actions=[{"type": "flag", "message": "Privacy clause required"}]
            ),
            ComplianceRule(
                id="rule2",
                name="Corporate Liability Rule",
                conditions=[{"field": "client_type", "operator": "equals", "value": "corporate"}],
                actions=[{"type": "flag", "message": "Liability clause required"}]
            )
        ]
        rule_engine._get_applicable_rules.return_value = rules
        
        # Mock _evaluate_rule
        rule_engine._evaluate_rule = AsyncMock(side_effect=[
            {"rule_id": "rule1", "result": "passed"},
            {"rule_id": "rule2", "result": "flagged", "message": "Liability clause required"}
        ])
        
        # Act
        results = await rule_engine.evaluate_rules(document, jurisdiction, context)
        
        # Assert
        assert len(results) == 2
        assert results[0]["rule_id"] == "rule1"
        assert results[1]["rule_id"] == "rule2"
        assert results[1]["message"] == "Liability clause required"
        
        rule_engine._get_applicable_rules.assert_called_once_with(jurisdiction, document["type"])
        assert rule_engine._evaluate_rule.call_count == 2
    
    @pytest.mark.asyncio
    async def test_evaluate_rule(self, rule_engine):
        # Arrange
        document = {
            "id": "doc123",
            "type": "contract",
            "content": "Sample contract content with privacy clause"
        }
        context = {"client_type": "corporate"}
        
        rule = ComplianceRule(
            id="rule1",
            name="Privacy Rule",
            conditions=[{"field": "content", "operator": "contains", "value": "privacy"}],
            actions=[{"type": "flag", "message": "Privacy clause detected"}]
        )
        
        # Mock rule parser
        parsed_conditions = [
            RuleCondition(field="content", operator="contains", value="privacy")
        ]
        rule_engine.rule_parser.parse_conditions.return_value = parsed_conditions
        
        parsed_actions = [
            RuleAction(type="flag", message="Privacy clause detected")
        ]
        rule_engine.rule_parser.parse_actions.return_value = parsed_actions
        
        # Mock _check_conditions and _execute_actions
        rule_engine._check_conditions = AsyncMock(return_value=True)
        rule_engine._execute_actions = AsyncMock(return_value={
            "rule_id": "rule1",
            "result": "flagged",
            "message": "Privacy clause detected"
        })
        
        # Restore original method for testing
        rule_engine._evaluate_rule = RuleEngine._evaluate_rule
        
        # Act
        result = await rule_engine._evaluate_rule(rule, document, context)
        
        # Assert
        assert result is not None
        assert result["rule_id"] == "rule1"
        assert result["result"] == "flagged"
        
        rule_engine.rule_parser.parse_conditions.assert_called_once_with(rule.conditions)
        rule_engine._check_conditions.assert_called_once_with(parsed_conditions, document, context)
        rule_engine.rule_parser.parse_actions.assert_called_once_with(rule.actions)
        rule_engine._execute_actions.assert_called_once_with(parsed_actions, document)
    
    @pytest.mark.asyncio
    async def test_check_conditions_all_match(self, rule_engine):
        # Arrange
        document = {
            "id": "doc123",
            "type": "contract",
            "content": "Sample contract with privacy clause"
        }
        context = {"client_type": "corporate"}
        
        conditions = [
            RuleCondition(field="content", operator="contains", value="privacy"),
            RuleCondition(field="client_type", operator="equals", value="corporate")
        ]
        
        # Restore original method for testing
        rule_engine._check_conditions = RuleEngine._check_conditions
        
        # Act
        result = await rule_engine._check_conditions(conditions, document, context)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_conditions_partial_match(self, rule_engine):
        # Arrange
        document = {
            "id": "doc123",
            "type": "contract",
            "content": "Sample contract with privacy clause"
        }
        context = {"client_type": "individual"}
        
        conditions = [
            RuleCondition(field="content", operator="contains", value="privacy"),
            RuleCondition(field="client_type", operator="equals", value="corporate")
        ]
        
        # Restore original method for testing
        rule_engine._check_conditions = RuleEngine._check_conditions
        
        # Act
        result = await rule_engine._check_conditions(conditions, document, context)
        
        # Assert
        assert result is False 