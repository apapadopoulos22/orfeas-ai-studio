"""
ORFEAS AI 2D→3D Studio - Model Selector
========================================
Advanced context-aware model selection with A/B testing and optimization.

Features:
- Context-aware model selection
- Performance vs cost optimization
- Real-time model health monitoring
- A/B testing framework
- Model recommendation engine
- Historical performance analysis
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import random
import json

from .llm_router import get_llm_router, TaskType, ModelProvider

logger = logging.getLogger(__name__)


class SelectionStrategy(Enum):
    """Model selection strategies"""
    BEST_PERFORMANCE = "best_performance"
    LOWEST_COST = "lowest_cost"
    BALANCED = "balanced"
    FASTEST = "fastest"
    MOST_RELIABLE = "most_reliable"
    A_B_TEST = "a_b_test"


@dataclass
class SelectionCriteria:
    """Criteria for model selection"""
    task_type: TaskType
    priority: str = "normal"  # low, normal, high, critical
    max_cost: Optional[float] = None
    max_latency_ms: Optional[int] = None
    min_quality: float = 0.7
    require_streaming: bool = False
    require_function_calling: bool = False
    strategy: SelectionStrategy = SelectionStrategy.BALANCED


@dataclass
class ModelRecommendation:
    """Model recommendation with reasoning"""
    model_id: str
    confidence: float
    reasoning: str
    expected_cost: float
    expected_latency_ms: float
    expected_quality: float
    alternatives: List[str] = field(default_factory=list)


@dataclass
class ABTestConfig:
    """Configuration for A/B testing"""
    test_id: str
    model_a: str
    model_b: str
    traffic_split: float = 0.5  # 50/50 split
    duration_hours: int = 24
    min_samples: int = 100
    start_time: datetime = field(default_factory=datetime.utcnow)
    active: bool = True


@dataclass
class ABTestResult:
    """Results from A/B test"""
    test_id: str
    model_a: str
    model_b: str
    model_a_samples: int
    model_b_samples: int
    model_a_avg_latency: float
    model_b_avg_latency: float
    model_a_success_rate: float
    model_b_success_rate: float
    model_a_avg_cost: float
    model_b_avg_cost: float
    winner: str
    confidence: float
    recommendation: str


class ModelSelector:
    """
    Advanced model selection with context awareness and A/B testing
    """

    def __init__(self):
        self.router = get_llm_router()
        self.selection_history: List[Dict[str, Any]] = []
        self.ab_tests: Dict[str, ABTestConfig] = {}
        self.ab_test_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.model_health: Dict[str, float] = {}

        # Configuration
        self.enable_ab_testing = True
        self.enable_health_monitoring = True
        self.health_check_interval = 60  # seconds

        # Start health monitoring
        if self.enable_health_monitoring:
            asyncio.create_task(self._health_monitoring_loop())

        logger.info("[ORFEAS-MODEL-SELECTOR] Model Selector initialized")

    async def select_model(
        self,
        criteria: SelectionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelRecommendation:
        """
        Select optimal model based on criteria and context

        Args:
            criteria: Selection criteria
            context: Additional context for selection

        Returns:
            ModelRecommendation with selected model and reasoning
        """
        try:
            # Check for active A/B test
            if self.enable_ab_testing:
                ab_model = await self._check_ab_test(criteria)
                if ab_model:
                    return ab_model

            # Select based on strategy
            if criteria.strategy == SelectionStrategy.BEST_PERFORMANCE:
                recommendation = await self._select_best_performance(criteria, context)
            elif criteria.strategy == SelectionStrategy.LOWEST_COST:
                recommendation = await self._select_lowest_cost(criteria, context)
            elif criteria.strategy == SelectionStrategy.BALANCED:
                recommendation = await self._select_balanced(criteria, context)
            elif criteria.strategy == SelectionStrategy.FASTEST:
                recommendation = await self._select_fastest(criteria, context)
            elif criteria.strategy == SelectionStrategy.MOST_RELIABLE:
                recommendation = await self._select_most_reliable(criteria, context)
            else:
                recommendation = await self._select_balanced(criteria, context)

            # Track selection
            self._track_selection(criteria, recommendation, context)

            logger.info(
                f"[ORFEAS-MODEL-SELECTOR] Selected {recommendation.model_id} "
                f"with {recommendation.confidence:.2f} confidence"
            )

            return recommendation

        except Exception as e:
            logger.error(f"[ORFEAS-MODEL-SELECTOR] Selection failed: {e}")

            # Fallback to router's default selection
            from .llm_router import RoutingContext
            routing_context = RoutingContext(
                task_type=criteria.task_type,
                prompt_length=1000,
                max_tokens=2000,
                priority=criteria.priority
            )

            model_id, model_config = await self.router.route_request("", routing_context)

            return ModelRecommendation(
                model_id=model_id,
                confidence=0.5,
                reasoning="Fallback selection due to error",
                expected_cost=0.0,
                expected_latency_ms=model_config.average_latency_ms,
                expected_quality=0.7
            )

    async def _select_best_performance(
        self,
        criteria: SelectionCriteria,
        context: Optional[Dict[str, Any]]
    ) -> ModelRecommendation:
        """Select model with best historical performance"""

        candidates = self._get_candidate_models(criteria)

        if not candidates:
            raise ValueError("No suitable models found")

        # Score by success rate and quality
        best_model = None
        best_score = -1.0

        for model_id in candidates:
            perf = self.router.get_model_performance(model_id)
            if perf and perf.total_requests > 0:
                success_rate = perf.successful_requests / perf.total_requests
                quality_estimate = 1.0 - perf.error_rate
                score = (success_rate * 0.6) + (quality_estimate * 0.4)

                if score > best_score:
                    best_score = score
                    best_model = model_id

        if not best_model:
            best_model = candidates[0]
            best_score = 0.8

        model_config = self.router.models[best_model]

        return ModelRecommendation(
            model_id=best_model,
            confidence=best_score,
            reasoning="Selected for highest historical performance metrics",
            expected_cost=self._estimate_cost(model_config),
            expected_latency_ms=model_config.average_latency_ms,
            expected_quality=best_score,
            alternatives=candidates[1:4]
        )

    async def _select_lowest_cost(
        self,
        criteria: SelectionCriteria,
        context: Optional[Dict[str, Any]]
    ) -> ModelRecommendation:
        """Select most cost-effective model"""

        candidates = self._get_candidate_models(criteria)

        if not candidates:
            raise ValueError("No suitable models found")

        # Find lowest cost model
        lowest_cost = float('inf')
        cheapest_model = None

        for model_id in candidates:
            model_config = self.router.models[model_id]
            avg_cost = (model_config.cost_per_1k_tokens_input +
                       model_config.cost_per_1k_tokens_output) / 2

            if avg_cost < lowest_cost:
                lowest_cost = avg_cost
                cheapest_model = model_id

        if not cheapest_model:
            cheapest_model = candidates[0]

        model_config = self.router.models[cheapest_model]

        return ModelRecommendation(
            model_id=cheapest_model,
            confidence=0.9,
            reasoning="Selected for lowest cost per token",
            expected_cost=self._estimate_cost(model_config),
            expected_latency_ms=model_config.average_latency_ms,
            expected_quality=0.75,
            alternatives=candidates[1:4]
        )

    async def _select_balanced(
        self,
        criteria: SelectionCriteria,
        context: Optional[Dict[str, Any]]
    ) -> ModelRecommendation:
        """Select balanced model (cost vs performance)"""

        candidates = self._get_candidate_models(criteria)

        if not candidates:
            raise ValueError("No suitable models found")

        # Score by balance of cost, performance, and latency
        best_model = None
        best_score = -1.0

        for model_id in candidates:
            model_config = self.router.models[model_id]
            perf = self.router.get_model_performance(model_id)

            # Cost score (lower is better)
            avg_cost = (model_config.cost_per_1k_tokens_input +
                       model_config.cost_per_1k_tokens_output) / 2
            cost_score = 1.0 / (1.0 + avg_cost * 100)  # Normalize

            # Performance score
            if perf and perf.total_requests > 0:
                perf_score = perf.successful_requests / perf.total_requests
            else:
                perf_score = 0.8

            # Latency score (lower is better)
            latency_score = 1.0 / (1.0 + model_config.average_latency_ms / 1000)

            # Balanced score
            score = (cost_score * 0.3) + (perf_score * 0.4) + (latency_score * 0.3)

            if score > best_score:
                best_score = score
                best_model = model_id

        if not best_model:
            best_model = candidates[0]
            best_score = 0.75

        model_config = self.router.models[best_model]

        return ModelRecommendation(
            model_id=best_model,
            confidence=best_score,
            reasoning="Selected for optimal balance of cost, performance, and latency",
            expected_cost=self._estimate_cost(model_config),
            expected_latency_ms=model_config.average_latency_ms,
            expected_quality=best_score,
            alternatives=candidates[1:4]
        )

    async def _select_fastest(
        self,
        criteria: SelectionCriteria,
        context: Optional[Dict[str, Any]]
    ) -> ModelRecommendation:
        """Select fastest responding model"""

        candidates = self._get_candidate_models(criteria)

        if not candidates:
            raise ValueError("No suitable models found")

        # Find fastest model
        fastest_model = min(
            candidates,
            key=lambda m: self.router.models[m].average_latency_ms
        )

        model_config = self.router.models[fastest_model]

        return ModelRecommendation(
            model_id=fastest_model,
            confidence=0.85,
            reasoning="Selected for lowest average latency",
            expected_cost=self._estimate_cost(model_config),
            expected_latency_ms=model_config.average_latency_ms,
            expected_quality=0.75,
            alternatives=candidates[1:4]
        )

    async def _select_most_reliable(
        self,
        criteria: SelectionCriteria,
        context: Optional[Dict[str, Any]]
    ) -> ModelRecommendation:
        """Select most reliable model (lowest error rate)"""

        candidates = self._get_candidate_models(criteria)

        if not candidates:
            raise ValueError("No suitable models found")

        # Find most reliable
        most_reliable = None
        lowest_error_rate = float('inf')

        for model_id in candidates:
            perf = self.router.get_model_performance(model_id)
            if perf and perf.total_requests > 0:
                if perf.error_rate < lowest_error_rate:
                    lowest_error_rate = perf.error_rate
                    most_reliable = model_id

        if not most_reliable:
            most_reliable = candidates[0]

        model_config = self.router.models[most_reliable]

        return ModelRecommendation(
            model_id=most_reliable,
            confidence=1.0 - lowest_error_rate,
            reasoning="Selected for lowest error rate and highest reliability",
            expected_cost=self._estimate_cost(model_config),
            expected_latency_ms=model_config.average_latency_ms,
            expected_quality=1.0 - lowest_error_rate,
            alternatives=candidates[1:4]
        )

    def _get_candidate_models(self, criteria: SelectionCriteria) -> List[str]:
        """Get candidate models meeting criteria"""

        candidates = []

        for model_id, config in self.router.models.items():
            # Check if enabled
            if not config.enabled:
                continue

            # Check health
            if self.enable_health_monitoring:
                health = self.model_health.get(model_id, 1.0)
                if health < 0.5:
                    continue

            # Check capabilities
            if criteria.task_type not in config.capabilities:
                continue

            # Check requirements
            if criteria.require_streaming and not config.supports_streaming:
                continue

            if criteria.require_function_calling and not config.supports_function_calling:
                continue

            # Check constraints
            if criteria.max_latency_ms and config.average_latency_ms > criteria.max_latency_ms:
                continue

            candidates.append(model_id)

        return candidates

    def _estimate_cost(self, model_config) -> float:
        """Estimate cost for typical request"""
        # Assume 1000 input tokens, 500 output tokens
        input_cost = (1000 / 1000) * model_config.cost_per_1k_tokens_input
        output_cost = (500 / 1000) * model_config.cost_per_1k_tokens_output
        return input_cost + output_cost

    async def _check_ab_test(self, criteria: SelectionCriteria) -> Optional[ModelRecommendation]:
        """Check if request should participate in A/B test"""

        # Find active A/B test for this task type
        for test_id, config in self.ab_tests.items():
            if not config.active:
                continue

            # Check if test expired
            elapsed = datetime.utcnow() - config.start_time
            if elapsed.total_seconds() / 3600 > config.duration_hours:
                config.active = False
                continue

            # Randomly assign to A or B based on traffic split
            if random.random() < config.traffic_split:
                selected_model = config.model_a
            else:
                selected_model = config.model_b

            model_config = self.router.models[selected_model]

            return ModelRecommendation(
                model_id=selected_model,
                confidence=0.8,
                reasoning=f"Selected as part of A/B test: {test_id}",
                expected_cost=self._estimate_cost(model_config),
                expected_latency_ms=model_config.average_latency_ms,
                expected_quality=0.8
            )

        return None

    def start_ab_test(
        self,
        model_a: str,
        model_b: str,
        duration_hours: int = 24,
        traffic_split: float = 0.5
    ) -> str:
        """Start A/B test between two models"""

        test_id = f"ab_test_{int(time.time())}"

        config = ABTestConfig(
            test_id=test_id,
            model_a=model_a,
            model_b=model_b,
            traffic_split=traffic_split,
            duration_hours=duration_hours
        )

        self.ab_tests[test_id] = config

        logger.info(
            f"[ORFEAS-MODEL-SELECTOR] Started A/B test {test_id}: "
            f"{model_a} vs {model_b}"
        )

        return test_id

    def track_ab_test_result(
        self,
        test_id: str,
        model_id: str,
        success: bool,
        latency_ms: float,
        cost: float
    ):
        """Track result for A/B test"""

        if test_id not in self.ab_tests:
            return

        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'model_id': model_id,
            'success': success,
            'latency_ms': latency_ms,
            'cost': cost
        }

        self.ab_test_results[test_id].append(result)

    def analyze_ab_test(self, test_id: str) -> Optional[ABTestResult]:
        """Analyze A/B test results"""

        if test_id not in self.ab_tests:
            return None

        config = self.ab_tests[test_id]
        results = self.ab_test_results[test_id]

        if len(results) < config.min_samples:
            logger.warning(
                f"[ORFEAS-MODEL-SELECTOR] Insufficient samples for {test_id}: "
                f"{len(results)}/{config.min_samples}"
            )
            return None

        # Separate results by model
        model_a_results = [r for r in results if r['model_id'] == config.model_a]
        model_b_results = [r for r in results if r['model_id'] == config.model_b]

        # Calculate metrics for model A
        model_a_samples = len(model_a_results)
        model_a_successes = sum(1 for r in model_a_results if r['success'])
        model_a_success_rate = model_a_successes / model_a_samples if model_a_samples > 0 else 0
        model_a_avg_latency = sum(r['latency_ms'] for r in model_a_results) / model_a_samples if model_a_samples > 0 else 0
        model_a_avg_cost = sum(r['cost'] for r in model_a_results) / model_a_samples if model_a_samples > 0 else 0

        # Calculate metrics for model B
        model_b_samples = len(model_b_results)
        model_b_successes = sum(1 for r in model_b_results if r['success'])
        model_b_success_rate = model_b_successes / model_b_samples if model_b_samples > 0 else 0
        model_b_avg_latency = sum(r['latency_ms'] for r in model_b_results) / model_b_samples if model_b_samples > 0 else 0
        model_b_avg_cost = sum(r['cost'] for r in model_b_results) / model_b_samples if model_b_samples > 0 else 0

        # Determine winner
        model_a_score = (model_a_success_rate * 0.5) + ((1 / (1 + model_a_avg_latency / 1000)) * 0.3) + ((1 / (1 + model_a_avg_cost * 100)) * 0.2)
        model_b_score = (model_b_success_rate * 0.5) + ((1 / (1 + model_b_avg_latency / 1000)) * 0.3) + ((1 / (1 + model_b_avg_cost * 100)) * 0.2)

        if model_a_score > model_b_score:
            winner = config.model_a
            confidence = model_a_score / (model_a_score + model_b_score)
        else:
            winner = config.model_b
            confidence = model_b_score / (model_a_score + model_b_score)

        recommendation = f"Recommend {winner} with {confidence:.1%} confidence"

        return ABTestResult(
            test_id=test_id,
            model_a=config.model_a,
            model_b=config.model_b,
            model_a_samples=model_a_samples,
            model_b_samples=model_b_samples,
            model_a_avg_latency=model_a_avg_latency,
            model_b_avg_latency=model_b_avg_latency,
            model_a_success_rate=model_a_success_rate,
            model_b_success_rate=model_b_success_rate,
            model_a_avg_cost=model_a_avg_cost,
            model_b_avg_cost=model_b_avg_cost,
            winner=winner,
            confidence=confidence,
            recommendation=recommendation
        )

    async def _health_monitoring_loop(self):
        """Background loop for model health monitoring"""

        while True:
            try:
                await asyncio.sleep(self.health_check_interval)

                # Update health scores for each model
                for model_id in self.router.models.keys():
                    health = await self._check_model_health(model_id)
                    self.model_health[model_id] = health

            except Exception as e:
                logger.error(f"[ORFEAS-MODEL-SELECTOR] Health monitoring error: {e}")

    async def _check_model_health(self, model_id: str) -> float:
        """Check health of a specific model"""

        perf = self.router.get_model_performance(model_id)

        if not perf or perf.total_requests == 0:
            return 1.0  # Unknown health, assume healthy

        # Calculate health based on recent performance
        success_rate = perf.successful_requests / perf.total_requests
        error_penalty = perf.error_rate

        health = success_rate * (1.0 - error_penalty)

        return max(0.0, min(1.0, health))

    def _track_selection(
        self,
        criteria: SelectionCriteria,
        recommendation: ModelRecommendation,
        context: Optional[Dict[str, Any]]
    ):
        """Track selection decision for analytics"""

        decision = {
            'timestamp': datetime.utcnow().isoformat(),
            'model_id': recommendation.model_id,
            'task_type': criteria.task_type.value,
            'strategy': criteria.strategy.value,
            'confidence': recommendation.confidence,
            'reasoning': recommendation.reasoning,
            'expected_cost': recommendation.expected_cost,
            'expected_latency_ms': recommendation.expected_latency_ms
        }

        self.selection_history.append(decision)

    def get_selection_statistics(self) -> Dict[str, Any]:
        """Get selection statistics"""

        if not self.selection_history:
            return {'total_selections': 0}

        total = len(self.selection_history)

        # Count by model
        model_counts = defaultdict(int)
        for decision in self.selection_history:
            model_counts[decision['model_id']] += 1

        # Count by strategy
        strategy_counts = defaultdict(int)
        for decision in self.selection_history:
            strategy_counts[decision['strategy']] += 1

        return {
            'total_selections': total,
            'model_distribution': dict(model_counts),
            'strategy_distribution': dict(strategy_counts),
            'active_ab_tests': len([t for t in self.ab_tests.values() if t.active]),
            'avg_confidence': sum(d['confidence'] for d in self.selection_history) / total
        }


# Global selector instance
_selector_instance: Optional[ModelSelector] = None


def get_model_selector() -> ModelSelector:
    """Get global model selector instance"""
    global _selector_instance
    if _selector_instance is None:
        _selector_instance = ModelSelector()
    return _selector_instance
