"""
Token Counter Module - Token Usage and Cost Tracking

Purpose:
    Track and calculate token usage across different LLM models:
    - Model-specific token counting
    - Cost estimation per token/request
    - Budget tracking and alerts
    - Usage reporting and analytics
    - Token limit warnings

Performance Targets:
    - Token counting: <5ms
    - Cost calculation: <2ms
    - Budget check: <1ms
    - Total per-call: <10ms
"""

import logging
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .error_handler import (
    error_context,
    safe_execute,
    TokenCountError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers and models."""
    GPT4_TURBO = "gpt-4-turbo"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE3_OPUS = "claude-3-opus"
    CLAUDE3_SONNET = "claude-3-sonnet"
    MISTRAL_LARGE = "mistral-large"
    LLAMA2_70B = "llama2-70b"


@dataclass
class ModelPricing:
    """Pricing information for a model."""
    model: str
    input_tokens_per_dollar: float  # tokens per $1 (inverse pricing)
    output_tokens_per_dollar: float
    description: str = ""


@dataclass
class TokenUsage:
    """Token usage for a single request."""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost: float  # in dollars
    output_cost: float
    total_cost: float
    timestamp: datetime = field(default_factory=datetime.now)


class TokenCounter:
    """
    Token usage and cost tracking system.

    Tracks token usage across models and calculates associated costs.
    """

    # Model pricing as of October 2024 (tokens per $1)
    MODEL_PRICING = {
        "gpt-4-turbo": ModelPricing(
            model="gpt-4-turbo",
            input_tokens_per_dollar=40000,  # $0.000025 per token
            output_tokens_per_dollar=13333,  # $0.000075 per token
            description="GPT-4 Turbo (128K tokens)"
        ),
        "gpt-4": ModelPricing(
            model="gpt-4",
            input_tokens_per_dollar=20000,  # $0.00005 per token
            output_tokens_per_dollar=6666,  # $0.00015 per token
            description="GPT-4 (8K tokens)"
        ),
        "gpt-3.5-turbo": ModelPricing(
            model="gpt-3.5-turbo",
            input_tokens_per_dollar=400000,  # $0.0000025 per token
            output_tokens_per_dollar=133333,  # $0.0000075 per token
            description="GPT-3.5 Turbo (4K/16K)"
        ),
        "claude-3-opus": ModelPricing(
            model="claude-3-opus",
            input_tokens_per_dollar=100000,  # $0.00001 per token
            output_tokens_per_dollar=33333,  # $0.00003 per token
            description="Claude 3 Opus (200K tokens)"
        ),
        "claude-3-sonnet": ModelPricing(
            model="claude-3-sonnet",
            input_tokens_per_dollar=333333,  # $0.000003 per token
            output_tokens_per_dollar=111111,  # $0.000009 per token
            description="Claude 3 Sonnet (200K tokens)"
        ),
        "mistral-large": ModelPricing(
            model="mistral-large",
            input_tokens_per_dollar=500000,  # $0.000002 per token
            output_tokens_per_dollar=500000,  # $0.000002 per token
            description="Mistral Large (32K tokens)"
        ),
        "llama2-70b": ModelPricing(
            model="llama2-70b",
            input_tokens_per_dollar=1000000,  # $0.000001 per token
            output_tokens_per_dollar=1000000,  # $0.000001 per token
            description="Llama 2 70B (local or API)"
        ),
    }

    def __init__(self, budget_limit_usd: Optional[float] = None):
        """
        Initialize token counter.

        Args:
            budget_limit_usd: Optional budget limit in USD for alerts
        """
        self.budget_limit = budget_limit_usd
        self.usage_history: List[TokenUsage] = []
        self.daily_costs: Dict[str, float] = {}
        self.model_costs: Dict[str, float] = {}
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        logger.info(
            f"TokenCounter initialized "
            f"(budget_limit=${budget_limit_usd or 'unlimited'})"
        )

    @trace_performance(operation='count_tokens', component='token_counter')
    @error_context(component='token_counter', operation='count_tokens')
    def count_tokens(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> TokenUsage:
        """
        Count tokens and calculate cost.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            TokenUsage object with cost information
        """
        pricing = self.MODEL_PRICING.get(model)
        if not pricing:
            logger.warning(f"Unknown model: {model}, assuming $0.001 per 1K tokens")
            pricing = ModelPricing(
                model=model,
                input_tokens_per_dollar=1000000,
                output_tokens_per_dollar=1000000,
                description="Unknown model"
            )

        # Calculate costs
        input_cost = prompt_tokens / pricing.input_tokens_per_dollar
        output_cost = completion_tokens / pricing.output_tokens_per_dollar
        total_cost = input_cost + output_cost

        # Create usage record
        usage = TokenUsage(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
        )

        # Track usage
        self._track_usage(usage)

        # Check budget
        if self.budget_limit and self.get_total_cost() > self.budget_limit:
            logger.warning(
                f"Budget alert: ${self.get_total_cost():.4f} "
                f"exceeds limit ${self.budget_limit}"
            )

        return usage
    @trace_performance(operation='track_usage', component='token_counter')
    @error_context(component='token_counter', operation='track_usage')
    def _track_usage(self, usage: TokenUsage) -> None:
        """Track usage for analytics."""
        self.usage_history.append(usage)

        # Track daily costs
        day_key = usage.timestamp.strftime("%Y-%m-%d")
        self.daily_costs[day_key] = self.daily_costs.get(day_key, 0) + usage.total_cost

        # Track model costs
        self.model_costs[usage.model] = self.model_costs.get(usage.model, 0) + usage.total_cost

    def get_total_cost(self) -> float:
        """Get total cost across all usage."""
        return sum(u.total_cost for u in self.usage_history)

    def get_total_tokens(self) -> int:
        """Get total tokens across all usage."""
        return sum(u.total_tokens for u in self.usage_history)

    def get_daily_cost(self, date: Optional[str] = None) -> float:
        """
        Get cost for a specific day.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Cost in dollars
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.daily_costs.get(date, 0.0)

    def get_model_cost(self, model: str) -> float:
        """Get total cost for a specific model."""
        return self.model_costs.get(model, 0.0)

    def get_model_stats(self, model: str) -> Dict[str, Any]:
        """Get statistics for a specific model."""
        usage = [u for u in self.usage_history if u.model == model]

        if not usage:
            return {
                'model': model,
                'count': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
            }

        return {
            'model': model,
            'count': len(usage),
            'total_tokens': sum(u.total_tokens for u in usage),
            'avg_tokens': sum(u.total_tokens for u in usage) / len(usage),
            'total_cost': self.get_model_cost(model),
            'avg_cost': self.get_model_cost(model) / len(usage),
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage summary."""
        if not self.usage_history:
            return {
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'models_used': [],
            }

        return {
            'total_requests': len(self.usage_history),
            'total_tokens': self.get_total_tokens(),
            'total_cost': self.get_total_cost(),
            'avg_cost_per_request': self.get_total_cost() / len(self.usage_history),
            'models_used': list(self.model_costs.keys()),
            'budget_limit': self.budget_limit,
            'budget_remaining': (self.budget_limit - self.get_total_cost())
                                if self.budget_limit else None,
            'date_range': {
                'start': self.usage_history[0].timestamp.isoformat(),
                'end': self.usage_history[-1].timestamp.isoformat(),
            }
        }

    @trace_performance(operation='estimate_cost', component='token_counter')
    @error_context(component='token_counter', operation='estimate_cost')
    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Estimate cost without recording."""
        pricing = self.MODEL_PRICING.get(model)
        if not pricing:
            return 0.0

        input_cost = prompt_tokens / pricing.input_tokens_per_dollar
        output_cost = completion_tokens / pricing.output_tokens_per_dollar
        return input_cost + output_cost

    def get_budget_status(self) -> Dict[str, Any]:
        """Get budget status."""
        total_cost = self.get_total_cost()

        if not self.budget_limit:
            return {
                'budget_limit': None,
                'current_cost': total_cost,
                'remaining': None,
                'percentage_used': None,
                'alert': False,
            }

        remaining = self.budget_limit - total_cost
        percentage = (total_cost / self.budget_limit * 100) if self.budget_limit > 0 else 0

        return {
            'budget_limit': self.budget_limit,
            'current_cost': total_cost,
            'remaining': remaining,
            'percentage_used': percentage,
            'alert': percentage >= 80,  # Alert at 80%
        }

    def export_usage_report(self) -> List[Dict[str, Any]]:
        """Export detailed usage report."""
        return [
            {
                'model': u.model,
                'prompt_tokens': u.prompt_tokens,
                'completion_tokens': u.completion_tokens,
                'total_tokens': u.total_tokens,
                'input_cost': round(u.input_cost, 6),
                'output_cost': round(u.output_cost, 6),
                'total_cost': round(u.total_cost, 6),
                'timestamp': u.timestamp.isoformat(),
            }
            for u in self.usage_history
        ]

    def reset_history(self) -> None:
        """Clear all usage history."""
        self.usage_history = []
        self.daily_costs = {}
        self.model_costs = {}
        logger.info("Token counter history cleared")


# Global token counter instance
_token_counter: Optional[TokenCounter] = None


def get_token_counter(budget_limit: Optional[float] = None) -> TokenCounter:
    """Get or create global token counter instance."""
    global _token_counter
    if _token_counter is None:
        _token_counter = TokenCounter(budget_limit)
    return _token_counter
