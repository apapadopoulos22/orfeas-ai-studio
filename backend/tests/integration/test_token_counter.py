"""
Unit Tests for Token Counter (File 7)
Tests token counting, cost calculation, and budget tracking
"""

import pytest
from backend.llm_integration.token_counter import (
    TokenCounter,
    TokenUsage,
    ModelProvider,
)


class TestTokenCounter:
    """Test suite for TokenCounter class."""

    @pytest.fixture
    def counter(self):
        """Create fresh token counter for each test."""
        return TokenCounter(budget_limit=100.0)

    def test_counter_initialization(self, counter):
        """Test counter initializes correctly."""
        assert counter.budget_limit == 100.0
        assert len(counter.usage_history) == 0
        assert counter.get_total_cost() == 0.0

    def test_count_tokens_gpt4(self, counter):
        """Test token counting for GPT-4."""
        usage = counter.count_tokens("gpt-4-turbo", 500, 200)

        assert usage.model == "gpt-4-turbo"
        assert usage.prompt_tokens == 500
        assert usage.completion_tokens == 200
        assert usage.total_tokens == 700
        assert usage.total_cost > 0

    def test_count_tokens_gpt35(self, counter):
        """Test token counting for GPT-3.5."""
        usage = counter.count_tokens("gpt-3.5-turbo", 1000, 500)

        assert usage.model == "gpt-3.5-turbo"
        assert usage.total_cost > 0
        # GPT-3.5 should be cheaper than GPT-4
        assert usage.total_cost < 0.01

    def test_count_tokens_claude(self, counter):
        """Test token counting for Claude."""
        usage = counter.count_tokens("claude-3-sonnet", 1000, 500)

        assert usage.model == "claude-3-sonnet"
        assert usage.total_cost > 0

    def test_total_cost_calculation(self, counter):
        """Test total cost across multiple requests."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-3.5-turbo", 1000, 500)

        total_cost = counter.get_total_cost()
        assert total_cost > 0
        assert len(counter.usage_history) == 2

    def test_total_tokens_calculation(self, counter):
        """Test total tokens across multiple requests."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-3.5-turbo", 1000, 500)

        total_tokens = counter.get_total_tokens()
        assert total_tokens == 2200  # 500+200+1000+500

    def test_daily_cost_tracking(self, counter):
        """Test daily cost aggregation."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-4-turbo", 500, 200)

        daily_cost = counter.get_daily_cost()
        assert daily_cost > 0

    def test_model_cost_tracking(self, counter):
        """Test per-model cost tracking."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-3.5-turbo", 1000, 500)

        gpt4_cost = counter.get_model_cost("gpt-4-turbo")
        gpt35_cost = counter.get_model_cost("gpt-3.5-turbo")

        assert gpt4_cost > 0
        assert gpt35_cost > 0
        assert gpt4_cost != gpt35_cost

    def test_budget_limit_alert(self, counter):
        """Test budget limit alerting."""
        counter_small = TokenCounter(budget_limit=0.0001)  # Very small budget
        usage = counter_small.count_tokens("gpt-4-turbo", 500, 200)

        # Should trigger budget warning
        assert counter_small.get_total_cost() > counter_small.budget_limit

    def test_budget_status(self, counter):
        """Test budget status reporting."""
        counter.count_tokens("gpt-4-turbo", 500, 200)

        status = counter.get_budget_status()
        assert 'budget_limit' in status
        assert 'current_cost' in status
        assert 'remaining' in status
        assert status['percentage_used'] < 100

    def test_estimate_cost(self, counter):
        """Test cost estimation without recording."""
        estimated = counter.estimate_cost("gpt-4-turbo", 500, 200)
        actual_usage = counter.count_tokens("gpt-4-turbo", 500, 200)

        # Estimate should match actual
        assert abs(estimated - actual_usage.total_cost) < 0.0001

    def test_model_statistics(self, counter):
        """Test per-model statistics."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-4-turbo", 300, 100)

        stats = counter.get_model_stats("gpt-4-turbo")
        assert stats['count'] == 2
        assert stats['total_tokens'] == 1100
        assert stats['avg_tokens'] == 550

    def test_summary_statistics(self, counter):
        """Test comprehensive summary statistics."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-3.5-turbo", 1000, 500)

        summary = counter.get_summary_stats()
        assert summary['total_requests'] == 2
        assert summary['total_tokens'] == 2200
        assert len(summary['models_used']) == 2

    def test_export_usage_report(self, counter):
        """Test usage report export."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        counter.count_tokens("gpt-3.5-turbo", 1000, 500)

        report = counter.export_usage_report()
        assert len(report) == 2
        assert all('model' in r for r in report)
        assert all('total_cost' in r for r in report)

    def test_reset_history(self, counter):
        """Test history reset."""
        counter.count_tokens("gpt-4-turbo", 500, 200)
        assert len(counter.usage_history) == 1

        counter.reset_history()
        assert len(counter.usage_history) == 0
        assert counter.get_total_cost() == 0.0

    def test_unknown_model_handling(self, counter):
        """Test handling of unknown models."""
        # Should not raise, just use default pricing
        usage = counter.count_tokens("unknown-model-xyz", 500, 200)
        assert usage is not None


class TestTokenUsage:
    """Test suite for TokenUsage dataclass."""

    def test_token_usage_creation(self):
        """Test TokenUsage initialization."""
        usage = TokenUsage(
            model="gpt-4-turbo",
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700,
            input_cost=0.0125,
            output_cost=0.015,
            total_cost=0.0275
        )
        assert usage.total_tokens == 700
        assert usage.total_cost == 0.0275

    def test_token_usage_defaults(self):
        """Test TokenUsage with default timestamp."""
        usage = TokenUsage(
            model="test",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003
        )
        assert usage.timestamp is not None


class TestModelProvider:
    """Test suite for ModelProvider enum."""

    def test_model_provider_values(self):
        """Test all model provider enum values."""
        providers = [
            ModelProvider.GPT4_TURBO,
            ModelProvider.GPT4,
            ModelProvider.GPT35_TURBO,
            ModelProvider.CLAUDE3_OPUS,
            ModelProvider.CLAUDE3_SONNET,
            ModelProvider.MISTRAL_LARGE,
            ModelProvider.LLAMA2_70B,
        ]
        assert len(providers) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
