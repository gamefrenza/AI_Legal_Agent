from typing import Dict, Any, List, Optional
from .base_integration import BaseIntegration
from ..models.research import ResearchQuery, ResearchResult
from ..utils.query_builder import QueryBuilder

class LegalResearchIntegration(BaseIntegration):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.query_builder = QueryBuilder()
        
    async def search_cases(
        self,
        query: ResearchQuery,
        jurisdiction: Optional[str] = None
    ) -> List[ResearchResult]:
        """Search case law"""
        formatted_query = self.query_builder.build_case_query(query)
        
        response = await self.execute_request(
            method="POST",
            endpoint="/api/v1/cases/search",
            data={
                "query": formatted_query,
                "jurisdiction": jurisdiction,
                "filters": query.filters
            }
        )
        
        return [ResearchResult(**result) for result in response['results']]
    
    async def get_case_details(self, case_id: str) -> Dict[str, Any]:
        """Get detailed case information"""
        return await self.execute_request(
            method="GET",
            endpoint=f"/api/v1/cases/{case_id}"
        )
    
    async def save_research(
        self,
        research_data: Dict[str, Any],
        matter_id: Optional[str] = None
    ) -> str:
        """Save research results"""
        response = await self.execute_request(
            method="POST",
            endpoint="/api/v1/research",
            data={
                "research_data": research_data,
                "matter_id": matter_id
            }
        )
        return response['research_id'] 