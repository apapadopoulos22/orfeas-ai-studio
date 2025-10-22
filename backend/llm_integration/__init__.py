"""
ORFEAS LLM Integration Module

Phase 3.1: Enterprise LLM Capabilities
- Multi-LLM routing and orchestration
- Prompt optimization and semantic understanding
- Retrieval-Augmented Generation (RAG)
- Token counting and cost tracking
- Quality monitoring and failover
"""

from .llm_router import LLMRouter
from .multi_llm_orchestrator import MultiLLMOrchestrator

__all__ = [
    'LLMRouter',
    'MultiLLMOrchestrator',
]

__version__ = '3.1.0'
__phase__ = 'Phase 3.1: LLM Integration'
