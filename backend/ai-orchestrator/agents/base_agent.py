from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
from ..models.ai_config import AITask
from ..utils.performance_monitor import PerformanceMonitor

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.performance_monitor = PerformanceMonitor()
        self.error_handler = ErrorHandler()
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    async def execute(self, task: AITask) -> Dict[str, Any]:
        """Execute agent task with monitoring and error handling"""
        try:
            # Start performance monitoring
            with self.performance_monitor.track(self.__class__.__name__):
                # Pre-process
                processed_input = await self._preprocess_input(task.input_data)
                
                # Execute main processing
                result = await self.process(processed_input)
                
                # Post-process
                final_result = await self._postprocess_output(result)
                
                return final_result
                
        except Exception as e:
            await self.error_handler.handle(e, task)
            raise
    
    async def _preprocess_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process input data"""
        return input_data
    
    async def _postprocess_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process output data"""
        return output 