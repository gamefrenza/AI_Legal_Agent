from typing import Dict, Any
from datetime import datetime
import time
import statistics
from contextlib import contextmanager

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.current_tasks = {}
    
    @contextmanager
    def track(self, agent_name: str):
        """Track execution time and resources for an agent"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            # Record metrics
            self._record_metrics(
                agent_name,
                execution_time=end_time - start_time,
                memory_usage=end_memory - start_memory
            )
    
    def _record_metrics(
        self,
        agent_name: str,
        execution_time: float,
        memory_usage: float
    ) -> None:
        """Record performance metrics"""
        if agent_name not in self.metrics:
            self.metrics[agent_name] = {
                'execution_times': [],
                'memory_usage': [],
                'success_rate': 0,
                'error_rate': 0
            }
        
        metrics = self.metrics[agent_name]
        metrics['execution_times'].append(execution_time)
        metrics['memory_usage'].append(memory_usage)
    
    def get_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Get performance metrics for an agent"""
        metrics = self.metrics.get(agent_name, {})
        if not metrics:
            return {}
            
        return {
            'avg_execution_time': statistics.mean(metrics['execution_times']),
            'avg_memory_usage': statistics.mean(metrics['memory_usage']),
            'success_rate': metrics['success_rate'],
            'error_rate': metrics['error_rate']
        } 