from typing import Dict, Any, List
from .base_agent import BaseAgent
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import spacy
import numpy as np
from ..utils.risk_scorer import RiskScorer
from ..models.contract import ContractClause, RiskAssessment

class ContractReviewAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Load NLP models
        self.nlp = spacy.load("en_core_web_lg")
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.model = AutoModelForSequenceClassification.from_pretrained("nlpaueb/legal-bert-base-uncased")
        
        # Specialized pipelines
        self.clause_classifier = pipeline("text-classification", model="legal-bert-contract-clauses")
        self.risk_analyzer = pipeline("text-classification", model="legal-bert-risk-analysis")
        self.summarizer = pipeline("summarization", model="legal-bert-summarizer")
        
        # Utilities
        self.risk_scorer = RiskScorer()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process contract document"""
        document = input_data['document']
        context = input_data.get('context', {})
        
        # Analyze contract structure and extract clauses
        clauses = await self._extract_clauses(document)
        
        # Analyze each clause
        analyzed_clauses = []
        for clause in clauses:
            analysis = await self._analyze_clause(clause, context)
            analyzed_clauses.append(analysis)
        
        # Generate risk assessment
        risks = await self._assess_risks(analyzed_clauses)
        
        # Check compliance
        compliance_issues = await self._check_compliance(analyzed_clauses, context)
        
        # Generate summary and recommendations
        summary = await self._generate_summary(document, analyzed_clauses, risks)
        recommendations = await self._generate_recommendations(risks, compliance_issues)
        
        return {
            'clauses': analyzed_clauses,
            'risks': risks,
            'compliance_issues': compliance_issues,
            'summary': summary,
            'recommendations': recommendations
        }
    
    async def _extract_clauses(self, document: str) -> List[ContractClause]:
        """Extract and classify contract clauses"""
        # Split document into sections
        doc = self.nlp(document)
        sections = self._split_into_sections(doc)
        
        clauses = []
        for section in sections:
            # Classify section type
            clause_type = self.clause_classifier(section.text)[0]
            
            # Extract key terms
            terms = self._extract_terms(section)
            
            clause = ContractClause(
                text=section.text,
                type=clause_type['label'],
                confidence=clause_type['score'],
                terms=terms
            )
            clauses.append(clause)
        
        return clauses
    
    async def _analyze_clause(
        self,
        clause: ContractClause,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze individual clause"""
        # Perform deep analysis of clause
        analysis = {
            'clause': clause.dict(),
            'risk_factors': await self._identify_risk_factors(clause.text),
            'obligations': await self._extract_obligations(clause.text),
            'dependencies': await self._identify_dependencies(clause.text),
            'temporal_aspects': await self._extract_temporal_aspects(clause.text)
        }
        
        # Add context-specific analysis
        if context.get('jurisdiction'):
            analysis['jurisdiction_specific'] = await self._analyze_jurisdiction_compliance(
                clause.text,
                context['jurisdiction']
            )
        
        return analysis
    
    async def _assess_risks(self, analyzed_clauses: List[Dict]) -> List[RiskAssessment]:
        """Assess risks in contract clauses"""
        risks = []
        for clause_analysis in analyzed_clauses:
            # Get risk prediction
            risk_pred = self.risk_analyzer(clause_analysis['clause']['text'])[0]
            
            # Calculate risk score
            risk_score = self.risk_scorer.calculate_score(
                risk_pred['label'],
                risk_pred['score'],
                clause_analysis['risk_factors']
            )
            
            risk = RiskAssessment(
                clause_id=clause_analysis['clause']['id'],
                risk_level=risk_pred['label'],
                risk_score=risk_score,
                risk_factors=clause_analysis['risk_factors'],
                potential_impact=self._assess_potential_impact(risk_score, clause_analysis)
            )
            risks.append(risk)
        
        return risks
    
    async def _check_compliance(
        self,
        analyzed_clauses: List[Dict],
        context: Dict[str, Any]
    ) -> List[Dict]:
        """Check compliance with regulations and requirements"""
        compliance_issues = []
        
        # Get applicable regulations
        regulations = await self._get_applicable_regulations(context)
        
        for clause_analysis in analyzed_clauses:
            # Check against each regulation
            for regulation in regulations:
                issues = await self._check_regulation_compliance(
                    clause_analysis,
                    regulation
                )
                compliance_issues.extend(issues)
        
        return compliance_issues
    
    async def _generate_summary(
        self,
        document: str,
        analyzed_clauses: List[Dict],
        risks: List[RiskAssessment]
    ) -> Dict[str, Any]:
        """Generate contract summary with key points and risks"""
        # Generate overall summary
        summary_text = self.summarizer(document)[0]['summary_text']
        
        # Extract key points
        key_points = await self._extract_key_points(analyzed_clauses)
        
        # Summarize risks
        risk_summary = self._summarize_risks(risks)
        
        return {
            'summary': summary_text,
            'key_points': key_points,
            'risk_summary': risk_summary
        }
    
    async def _generate_recommendations(
        self,
        risks: List[RiskAssessment],
        compliance_issues: List[Dict]
    ) -> List[Dict]:
        """Generate recommendations for identified risks and issues"""
        recommendations = []
        
        # Generate risk-based recommendations
        for risk in risks:
            if risk.risk_score > self.config['risk_threshold']:
                rec = await self._generate_risk_recommendation(risk)
                recommendations.append(rec)
        
        # Generate compliance-based recommendations
        for issue in compliance_issues:
            rec = await self._generate_compliance_recommendation(issue)
            recommendations.append(rec)
        
        return recommendations
    
    def _split_into_sections(self, doc) -> List[Any]:
        """Split document into logical sections"""
        # Implementation using spaCy's section detection
        pass
    
    def _extract_terms(self, section) -> List[str]:
        """Extract key terms from section"""
        # Implementation using NER and term extraction
        pass 