from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime
from .models.compliance import ComplianceRule, RuleCondition, RuleAction
from .utils.rule_parser import RuleParser

class RuleEngine:
    def __init__(self):
        self.rule_parser = RuleParser()
        self.rules_cache = {}
        self.jurisdiction_rules = {}
    
    async def evaluate_rules(
        self,
        document: Dict[str, Any],
        jurisdiction: str,
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Evaluate document against applicable rules"""
        
        # Get applicable rules
        rules = await self._get_applicable_rules(jurisdiction, document['type'])
        
        # Evaluate each rule
        results = []
        for rule in rules:
            result = await self._evaluate_rule(rule, document, context)
            if result:
                results.append(result)
        
        return results
    
    async def _evaluate_rule(
        self,
        rule: ComplianceRule,
        document: Dict[str, Any],
        context: Optional[Dict]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a single rule against document"""
        
        try:
            # Parse rule conditions
            conditions = self.rule_parser.parse_conditions(rule.conditions)
            
            # Check if conditions match
            if await self._check_conditions(conditions, document, context):
                # Execute rule actions
                actions = self.rule_parser.parse_actions(rule.actions)
                result = await self._execute_actions(actions, document)
                
                return {
                    'rule_id': rule.id,
                    'status': 'violation' if result['is_violation'] else 'compliant',
                    'details': result['details'],
                    'severity': rule.severity,
                    'remediation': rule.remediation_steps
                }
        except Exception as e:
            # Log rule evaluation error
            return {
                'rule_id': rule.id,
                'status': 'error',
                'error': str(e)
            }
        
        return None
    
    async def _check_conditions(
        self,
        conditions: List[RuleCondition],
        document: Dict[str, Any],
        context: Optional[Dict]
    ) -> bool:
        """Check if document matches rule conditions"""
        for condition in conditions:
            if not await self._evaluate_condition(condition, document, context):
                return False
        return True
    
    async def _execute_actions(
        self,
        actions: List[RuleAction],
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute rule actions and return results"""
        results = {
            'is_violation': False,
            'details': []
        }
        
        for action in actions:
            action_result = await self._execute_action(action, document)
            if action_result['is_violation']:
                results['is_violation'] = True
                results['details'].append(action_result['details'])
        
        return results 