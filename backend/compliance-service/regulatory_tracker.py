from typing import Dict, List, Any
from datetime import datetime
import aiohttp
from .models.compliance import Regulation, RegulatoryUpdate
from .utils.diff_analyzer import DiffAnalyzer

class RegulatoryTracker:
    def __init__(self):
        self.diff_analyzer = DiffAnalyzer()
        self.regulatory_sources = {}
        
    async def track_updates(self, jurisdiction: str) -> List[RegulatoryUpdate]:
        """Track regulatory updates for jurisdiction"""
        
        # Get current regulations
        current = await self._get_current_regulations(jurisdiction)
        
        # Fetch latest updates
        updates = await self._fetch_regulatory_updates(jurisdiction)
        
        # Analyze changes
        changes = []
        for update in updates:
            diff = await self.diff_analyzer.analyze_changes(
                current.get(update.regulation_id),
                update
            )
            
            if diff.has_changes:
                changes.append(RegulatoryUpdate(
                    regulation_id=update.regulation_id,
                    jurisdiction=jurisdiction,
                    changes=diff.changes,
                    effective_date=update.effective_date,
                    impact_assessment=await self._assess_impact(diff.changes)
                ))
        
        # Store updates
        await self._store_updates(changes)
        
        return changes
    
    async def get_affected_documents(
        self,
        regulatory_update: RegulatoryUpdate
    ) -> List[Dict[str, Any]]:
        """Get documents affected by regulatory update"""
        
        # Query documents under jurisdiction
        documents = await self._get_jurisdiction_documents(
            regulatory_update.jurisdiction
        )
        
        # Analyze impact on each document
        affected = []
        for doc in documents:
            impact = await self._analyze_document_impact(
                doc,
                regulatory_update
            )
            if impact['is_affected']:
                affected.append({
                    'document_id': doc['id'],
                    'impact': impact['details']
                })
        
        return affected 