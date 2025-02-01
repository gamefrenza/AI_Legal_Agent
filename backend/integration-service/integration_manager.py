from typing import Dict, Any, List
from .interfaces import (
    LegalResearchIntegration,
    DocumentManagementIntegration,
    ESignatureIntegration
)
from .models.integration import IntegrationConfig
from .utils.config_validator import ConfigValidator

class IntegrationManager:
    def __init__(self):
        self.config_validator = ConfigValidator()
        self.integrations = {}
        
    async def register_integration(
        self,
        integration_type: str,
        config: IntegrationConfig
    ) -> None:
        """Register new integration"""
        # Validate configuration
        if not await self.config_validator.validate(integration_type, config):
            raise ValueError("Invalid integration configuration")
        
        # Create integration instance
        integration = self._create_integration(integration_type, config)
        
        # Test connection
        if not await integration.connect():
            raise ConnectionError("Failed to connect to integration")
        
        # Store integration
        self.integrations[config.integration_id] = integration
    
    def _create_integration(
        self,
        integration_type: str,
        config: IntegrationConfig
    ) -> BaseIntegration:
        """Create integration instance based on type"""
        integration_classes = {
            'legal_research': LegalResearchIntegration,
            'document_management': DocumentManagementIntegration,
            'esignature': ESignatureIntegration
        }
        
        if integration_type not in integration_classes:
            raise ValueError(f"Unknown integration type: {integration_type}")
            
        return integration_classes[integration_type](config.dict())
    
    async def get_integration(
        self,
        integration_id: str
    ) -> BaseIntegration:
        """Get integration instance"""
        if integration_id not in self.integrations:
            raise ValueError(f"Integration not found: {integration_id}")
            
        return self.integrations[integration_id] 