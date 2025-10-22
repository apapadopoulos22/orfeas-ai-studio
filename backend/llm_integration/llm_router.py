"""
ORFEAS AI 2D→3D Studio - LLM Router
===================================
Intelligent routing and selection system for Large Language Models.

Features:
- Multi-model support (GPT-4, Claude, Gemini, Llama, Mistral)
- Context-aware model selection
- Automatic fallback strategies
- Performance tracking and optimization
- Cost management and budgeting
- Load balancing across models
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import json

from backend.llm_integration.error_handler import (
    error_context,
    safe_execute,
    LLMRouterError,
    ErrorAggregator
)
from backend.llm_integration.tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    MISTRAL = "mistral"
    COHERE = "cohere"
    AZURE = "azure"
    LOCAL = "local"


class TaskType(Enum):
    """Types of tasks for model selection"""
    CODE_GENERATION = "code_generation"
    TEXT_ANALYSIS = "text_analysis"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "qa"
    CHAT = "chat"
    MULTIMODAL = "multimodal"
    GENERAL = "general"


@dataclass
class ModelConfig:
    """Configuration for an LLM model"""
    model_id: str
    provider: ModelProvider
    display_name: str
    max_tokens: int
    cost_per_1k_tokens_input: float
    cost_per_1k_tokens_output: float
    capabilities: List[TaskType]
    max_context_length: int
    supports_streaming: bool
    supports_function_calling: bool
    average_latency_ms: float = 1000.0
    priority: int = 1  # 1 = highest priority
    enabled: bool = True


@dataclass
class RoutingContext:
    """Context for routing decisions"""
    task_type: TaskType
    prompt_length: int
    max_tokens: int
    requires_streaming: bool = False
    requires_function_calling: bool = False
    budget_constraint: Optional[float] = None
    latency_requirement_ms: Optional[int] = None
    priority: str = "normal"  # low, normal, high, critical
    user_preference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelPerformance:
    """Track model performance metrics"""
    model_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cost: float = 0.0
    last_used: Optional[datetime] = None
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0


class LLMRouter:
    """
    Intelligent router for Large Language Model requests
    """

    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.performance: Dict[str, ModelPerformance] = {}
        self.routing_history = deque(maxlen=10000)
        self.fallback_chain: List[str] = []
        self.load_balancer_state: Dict[str, int] = defaultdict(int)

        # Error handling
        self.error_agg = ErrorAggregator()

        # Performance tracing
        self.perf_tracer = PerformanceTracer()

        # Configuration
        self.enable_fallback = True
        self.enable_load_balancing = True
        self.enable_cost_optimization = True
        self.enable_performance_tracking = True

        # Initialize models
        self._initialize_models()

        logger.info("[ORFEAS-LLM] LLM Router initialized with %d models", len(self.models))

    def _initialize_models(self):
        """Initialize available LLM models"""

        # GPT-4 Turbo (OpenAI)
        self.register_model(ModelConfig(
            model_id="gpt-4-turbo",
            provider=ModelProvider.OPENAI,
            display_name="GPT-4 Turbo",
            max_tokens=4096,
            cost_per_1k_tokens_input=0.01,
            cost_per_1k_tokens_output=0.03,
            capabilities=[
                TaskType.CODE_GENERATION,
                TaskType.REASONING,
                TaskType.TEXT_ANALYSIS,
                TaskType.QUESTION_ANSWERING,
                TaskType.CHAT,
                TaskType.GENERAL
            ],
            max_context_length=128000,
            supports_streaming=True,
            supports_function_calling=True,
            average_latency_ms=2000,
            priority=1
        ))

        # Claude 3.5 Sonnet (Anthropic)
        self.register_model(ModelConfig(
            model_id="claude-3-5-sonnet",
            provider=ModelProvider.ANTHROPIC,
            display_name="Claude 3.5 Sonnet",
            max_tokens=4096,
            cost_per_1k_tokens_input=0.003,
            cost_per_1k_tokens_output=0.015,
            capabilities=[
                TaskType.CODE_GENERATION,
                TaskType.CREATIVE_WRITING,
                TaskType.TEXT_ANALYSIS,
                TaskType.REASONING,
                TaskType.CHAT
            ],
            max_context_length=200000,
            supports_streaming=True,
            supports_function_calling=True,
            average_latency_ms=1500,
            priority=1
        ))

        # Gemini Ultra (Google)
        self.register_model(ModelConfig(
            model_id="gemini-ultra",
            provider=ModelProvider.GOOGLE,
            display_name="Gemini Ultra",
            max_tokens=8192,
            cost_per_1k_tokens_input=0.002,
            cost_per_1k_tokens_output=0.01,
            capabilities=[
                TaskType.MULTIMODAL,
                TaskType.REASONING,
                TaskType.TEXT_ANALYSIS,
                TaskType.QUESTION_ANSWERING,
                TaskType.GENERAL
            ],
            max_context_length=1000000,
            supports_streaming=True,
            supports_function_calling=True,
            average_latency_ms=2500,
            priority=2
        ))

        # Llama 3.1 405B (Meta)
        self.register_model(ModelConfig(
            model_id="llama-3-1-405b",
            provider=ModelProvider.META,
            display_name="Llama 3.1 405B",
            max_tokens=4096,
            cost_per_1k_tokens_input=0.0,  # Open source
            cost_per_1k_tokens_output=0.0,
            capabilities=[
                TaskType.CODE_GENERATION,
                TaskType.TEXT_ANALYSIS,
                TaskType.REASONING,
                TaskType.GENERAL
            ],
            max_context_length=128000,
            supports_streaming=True,
            supports_function_calling=False,
            average_latency_ms=3000,
            priority=3
        ))

        # Mistral 8x22B (Mistral AI)
        self.register_model(ModelConfig(
            model_id="mistral-8x22b",
            provider=ModelProvider.MISTRAL,
            display_name="Mistral 8x22B",
            max_tokens=4096,
            cost_per_1k_tokens_input=0.002,
            cost_per_1k_tokens_output=0.006,
            capabilities=[
                TaskType.CODE_GENERATION,
                TaskType.CHAT,
                TaskType.TEXT_ANALYSIS,
                TaskType.GENERAL
            ],
            max_context_length=64000,
            supports_streaming=True,
            supports_function_calling=True,
            average_latency_ms=1000,
            priority=2
        ))

    def register_model(self, config: ModelConfig):
        """Register a new LLM model"""
        self.models[config.model_id] = config
        self.performance[config.model_id] = ModelPerformance(model_id=config.model_id)
        logger.info(f"[ORFEAS-LLM] Registered model: {config.model_id}")

    @trace_performance(operation='route_request', component='llm_router')
    @error_context(component='llm_router', operation='route_request')
    async def route_request(
        self,
        prompt: str,
        context: RoutingContext,
        fallback_on_error: bool = True
    ) -> Tuple[str, ModelConfig]:
        """
        Route LLM request to optimal model

        Returns:
            Tuple of (model_id, model_config)
        """
        try:
            # Select optimal model
            selected_model_id = await self._select_optimal_model(context)

            if not selected_model_id:
                raise ValueError("No suitable model found for request")

            model_config = self.models[selected_model_id]

            # Update load balancer state
            if self.enable_load_balancing:
                self.load_balancer_state[selected_model_id] += 1

            # Track routing decision
            self._track_routing_decision(selected_model_id, context)

            logger.info(
                f"[ORFEAS-LLM] Routed {context.task_type.value} request to {selected_model_id}"
            )

            return selected_model_id, model_config

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Routing failed: {e}")

            if fallback_on_error and self.enable_fallback:
                return await self._get_fallback_model(context)

            raise
    @trace_performance(operation='select_optimal_model', component='llm_router')
    @error_context(component='llm_router', operation='select_optimal_model')
    async def _select_optimal_model(self, context: RoutingContext) -> Optional[str]:
        """Select optimal model based on context"""

        # Get candidate models
        candidates = self._get_candidate_models(context)

        if not candidates:
            logger.warning("[ORFEAS-LLM] No candidate models found")
            return None

        # Score each candidate
        scored_candidates = []
        for model_id in candidates:
            score = await self._calculate_model_score(model_id, context)
            scored_candidates.append((model_id, score))

        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Select best model
        best_model_id = scored_candidates[0][0]
        best_score = scored_candidates[0][1]

        logger.debug(
            f"[ORFEAS-LLM] Selected {best_model_id} with score {best_score:.3f}"
        )

        return best_model_id

    def _get_candidate_models(self, context: RoutingContext) -> List[str]:
        """Get candidate models that meet requirements"""

        candidates = []

        for model_id, config in self.models.items():
            # Check if model is enabled
            if not config.enabled:
                continue

            # Check task capability
            if context.task_type not in config.capabilities:
                continue

            # Check streaming requirement
            if context.requires_streaming and not config.supports_streaming:
                continue

            # Check function calling requirement
            if context.requires_function_calling and not config.supports_function_calling:
                continue

            # Check context length
            if context.prompt_length > config.max_context_length:
                continue

            # Check latency requirement
            if context.latency_requirement_ms:
                if config.average_latency_ms > context.latency_requirement_ms:
                    continue

            # Check user preference
            if context.user_preference and context.user_preference != model_id:
                continue

            candidates.append(model_id)

        return candidates

    @trace_performance(operation='calculate_model_score', component='llm_router')
    @error_context(component='llm_router', operation='calculate_model_score')
    async def _calculate_model_score(
        self,
        model_id: str,
        context: RoutingContext
    ) -> float:
        """Calculate score for model selection"""

        config = self.models[model_id]
        perf = self.performance[model_id]

        score = 0.0

        # Priority score (40% weight)
        priority_score = (5 - config.priority) / 4  # Normalize to 0-1
        score += priority_score * 0.4

        # Performance score (30% weight)
        if perf.total_requests > 0:
            success_rate = perf.successful_requests / perf.total_requests
            error_penalty = 1.0 - perf.error_rate
            performance_score = (success_rate + error_penalty) / 2
        else:
            performance_score = 0.8  # Default for untested models
        score += performance_score * 0.3

        # Cost score (20% weight) - if cost optimization enabled
        if self.enable_cost_optimization and context.budget_constraint:
            estimated_cost = self._estimate_request_cost(config, context)
            if estimated_cost <= context.budget_constraint:
                cost_score = 1.0 - (estimated_cost / context.budget_constraint)
            else:
                cost_score = 0.0  # Over budget
            score += cost_score * 0.2
        else:
            score += 0.2  # No cost penalty

        # Latency score (10% weight)
        if context.latency_requirement_ms:
            if config.average_latency_ms <= context.latency_requirement_ms:
                latency_score = 1.0 - (config.average_latency_ms / context.latency_requirement_ms)
            else:
                latency_score = 0.0
        else:
            # Prefer faster models
            latency_score = 1.0 - min(config.average_latency_ms / 5000, 1.0)
        score += latency_score * 0.1

        # Load balancing adjustment
        if self.enable_load_balancing:
            current_load = self.load_balancer_state.get(model_id, 0)
            max_load = max(self.load_balancer_state.values(), default=1)
            if max_load > 0:
                load_penalty = current_load / max_load * 0.1
                score -= load_penalty

        return max(0.0, min(1.0, score))

    def _estimate_request_cost(
        self,
        config: ModelConfig,
        context: RoutingContext
    ) -> float:
        """Estimate cost for a request"""

        # Estimate input tokens
        input_tokens = context.prompt_length / 4  # Rough estimate

        # Estimate output tokens
        output_tokens = context.max_tokens

        # Calculate cost
        input_cost = (input_tokens / 1000) * config.cost_per_1k_tokens_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_tokens_output

        return input_cost + output_cost

    @trace_performance(operation='get_fallback_model', component='llm_router')
    @error_context(component='llm_router', operation='get_fallback_model')
    async def _get_fallback_model(
        self,
        context: RoutingContext
    ) -> Tuple[str, ModelConfig]:
        """Get fallback model when primary selection fails"""

        # Try fallback chain
        for model_id in self.fallback_chain:
            if model_id in self.models and self.models[model_id].enabled:
                config = self.models[model_id]
                logger.warning(f"[ORFEAS-LLM] Using fallback model: {model_id}")
                return model_id, config

        # Last resort: any enabled model
        for model_id, config in self.models.items():
            if config.enabled:
                logger.warning(f"[ORFEAS-LLM] Using last-resort model: {model_id}")
                return model_id, config

        raise RuntimeError("No fallback models available")

    def _track_routing_decision(self, model_id: str, context: RoutingContext):
        """Track routing decision for analytics"""

        decision = {
            'timestamp': datetime.utcnow().isoformat(),
            'model_id': model_id,
            'task_type': context.task_type.value,
            'priority': context.priority,
            'prompt_length': context.prompt_length,
            'max_tokens': context.max_tokens
        }

        self.routing_history.append(decision)

    def track_request_completion(
        self,
        model_id: str,
        success: bool,
        latency_ms: float,
        tokens_input: int,
        tokens_output: int,
        error: Optional[str] = None
    ):
        """Track completion of LLM request"""

        if not self.enable_performance_tracking:
            return

        if model_id not in self.performance:
            return

        perf = self.performance[model_id]
        config = self.models[model_id]

        # Update counters
        perf.total_requests += 1
        if success:
            perf.successful_requests += 1
        else:
            perf.failed_requests += 1

        # Update latency
        perf.total_latency_ms += latency_ms
        perf.avg_latency_ms = perf.total_latency_ms / perf.total_requests

        # Update error rate
        perf.error_rate = perf.failed_requests / perf.total_requests

        # Update tokens
        perf.total_tokens_input += tokens_input
        perf.total_tokens_output += tokens_output

        # Update cost
        input_cost = (tokens_input / 1000) * config.cost_per_1k_tokens_input
        output_cost = (tokens_output / 1000) * config.cost_per_1k_tokens_output
        perf.total_cost += input_cost + output_cost

        # Update last used
        perf.last_used = datetime.utcnow()

        # Update average latency in config (for future routing)
        config.average_latency_ms = perf.avg_latency_ms

        logger.debug(
            f"[ORFEAS-LLM] Tracked completion for {model_id}: "
            f"success={success}, latency={latency_ms}ms"
        )

    def set_fallback_chain(self, model_ids: List[str]):
        """Set fallback chain for model failures"""
        self.fallback_chain = model_ids
        logger.info(f"[ORFEAS-LLM] Fallback chain updated: {model_ids}")

    def enable_model(self, model_id: str):
        """Enable a model for routing"""
        if model_id in self.models:
            self.models[model_id].enabled = True
            logger.info(f"[ORFEAS-LLM] Enabled model: {model_id}")

    def disable_model(self, model_id: str):
        """Disable a model from routing"""
        if model_id in self.models:
            self.models[model_id].enabled = False
            logger.warning(f"[ORFEAS-LLM] Disabled model: {model_id}")

    def get_model_performance(self, model_id: str) -> Optional[ModelPerformance]:
        """Get performance metrics for a model"""
        return self.performance.get(model_id)

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics"""

        total_requests = sum(p.total_requests for p in self.performance.values())
        total_cost = sum(p.total_cost for p in self.performance.values())

        model_usage = {}
        for model_id, perf in self.performance.items():
            if perf.total_requests > 0:
                model_usage[model_id] = {
                    'requests': perf.total_requests,
                    'success_rate': perf.successful_requests / perf.total_requests,
                    'avg_latency_ms': perf.avg_latency_ms,
                    'total_cost': perf.total_cost,
                    'error_rate': perf.error_rate
                }

        return {
            'total_requests': total_requests,
            'total_cost': total_cost,
            'enabled_models': len([m for m in self.models.values() if m.enabled]),
            'model_usage': model_usage,
            'routing_history_size': len(self.routing_history)
        }

    def reset_performance_metrics(self):
        """Reset all performance metrics"""
        for model_id in self.performance:
            self.performance[model_id] = ModelPerformance(model_id=model_id)
        logger.info("[ORFEAS-LLM] Performance metrics reset")


# Global router instance
_router_instance: Optional[LLMRouter] = None


def get_llm_router() -> LLMRouter:
    """Get global LLM router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance
