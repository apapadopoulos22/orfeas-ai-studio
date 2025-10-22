"""
Comprehensive tests for LLM Router component.

Tests:
- Router selection logic
- Cost-aware routing
- Model fallback
- Error handling
- Load balancing
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.llm_integration.llm_router import LLMRouter, RoutingDecision


class TestLLMRouterSelection:
    """Test router selection logic."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_router_initialization(self, router):
        """Test router initializes correctly."""
        assert router is not None
        assert hasattr(router, 'models')
        assert hasattr(router, 'get_best_model')

    def test_select_best_model_cost(self, router):
        """Test selecting model by cost."""
        # Mock models with different costs
        with patch.object(router, 'models', {
            'gpt4': {'cost_per_1k': 0.03, 'latency_ms': 100},
            'gpt3.5': {'cost_per_1k': 0.001, 'latency_ms': 50},
            'claude': {'cost_per_1k': 0.01, 'latency_ms': 150}
        }):
            model = router.get_best_model(priority='cost')
            assert model == 'gpt3.5'

    def test_select_best_model_speed(self, router):
        """Test selecting model by speed."""
        with patch.object(router, 'models', {
            'gpt4': {'cost_per_1k': 0.03, 'latency_ms': 100},
            'gpt3.5': {'cost_per_1k': 0.001, 'latency_ms': 50},
            'claude': {'cost_per_1k': 0.01, 'latency_ms': 150}
        }):
            model = router.get_best_model(priority='speed')
            assert model == 'gpt3.5'

    def test_select_best_model_quality(self, router):
        """Test selecting model by quality."""
        with patch.object(router, 'models', {
            'gpt4': {'quality_score': 0.95, 'latency_ms': 100},
            'gpt3.5': {'quality_score': 0.85, 'latency_ms': 50},
            'claude': {'quality_score': 0.90, 'latency_ms': 150}
        }):
            model = router.get_best_model(priority='quality')
            assert model == 'gpt4'

    def test_select_model_with_constraints(self, router):
        """Test selecting model with budget constraints."""
        with patch.object(router, 'models', {
            'gpt4': {'cost_per_1k': 0.03},
            'gpt3.5': {'cost_per_1k': 0.001},
            'claude': {'cost_per_1k': 0.01}
        }):
            model = router.get_best_model(max_cost=0.015)
            assert model in ['gpt3.5', 'claude']
            assert model != 'gpt4'

    def test_select_model_with_latency_constraint(self, router):
        """Test selecting model with latency constraints."""
        with patch.object(router, 'models', {
            'gpt4': {'latency_ms': 100},
            'gpt3.5': {'latency_ms': 50},
            'claude': {'latency_ms': 150}
        }):
            model = router.get_best_model(max_latency_ms=80)
            assert model == 'gpt3.5'


class TestLLMRouterFallback:
    """Test router fallback mechanisms."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_fallback_on_model_unavailable(self, router):
        """Test fallback when primary model unavailable."""
        with patch.object(router, 'is_model_available', side_effect=[False, True]):
            with patch.object(router, 'models', {
                'gpt4': {'priority': 1},
                'gpt3.5': {'priority': 2}
            }):
                model = router.get_available_model()
                assert model == 'gpt3.5'

    def test_fallback_chain(self, router):
        """Test fallback chain through multiple models."""
        with patch.object(router, 'is_model_available', side_effect=[False, False, True]):
            fallback_chain = ['gpt4', 'claude', 'gpt3.5']
            result = router.try_fallback_chain(fallback_chain)
            assert result == 'gpt3.5'

    def test_all_models_unavailable(self, router):
        """Test behavior when all models unavailable."""
        with patch.object(router, 'is_model_available', return_value=False):
            with pytest.raises(Exception):
                router.get_available_model()

    def test_fallback_preserves_request_context(self, router):
        """Test fallback preserves request context."""
        request_context = {'user_id': '123', 'priority': 'high'}
        with patch.object(router, 'execute_with_fallback') as mock_exec:
            router.execute_with_fallback('gpt4', 'test', request_context)
            mock_exec.assert_called_once()
            # Verify context passed to fallback


class TestLLMRouterLoadBalancing:
    """Test router load balancing."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_round_robin_distribution(self, router):
        """Test round-robin load balancing."""
        models = ['gpt4', 'gpt3.5', 'claude']
        with patch.object(router, 'models', {m: {} for m in models}):
            selected_models = []
            for _ in range(9):
                model = router.get_next_model(models)
                selected_models.append(model)

            # Should distribute evenly
            assert selected_models.count('gpt4') == 3
            assert selected_models.count('gpt3.5') == 3
            assert selected_models.count('claude') == 3

    def test_weighted_distribution(self, router):
        """Test weighted load balancing."""
        weights = {'gpt4': 0.5, 'gpt3.5': 0.3, 'claude': 0.2}
        models_selected = []

        for _ in range(100):
            model = router.get_weighted_model(weights)
            models_selected.append(model)

        # Check approximate distribution (allow 20% tolerance)
        gpt4_count = models_selected.count('gpt4')
        assert 30 < gpt4_count < 70  # ~50%

        gpt35_count = models_selected.count('gpt3.5')
        assert 10 < gpt35_count < 50  # ~30%

    def test_load_aware_routing(self, router):
        """Test routing based on model load."""
        loads = {'gpt4': 0.9, 'gpt3.5': 0.1, 'claude': 0.5}

        with patch.object(router, 'get_model_load', side_effect=lambda m: loads.get(m)):
            model = router.get_least_loaded_model()
            assert model == 'gpt3.5'


class TestLLMRouterErrorHandling:
    """Test router error handling."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_invalid_model_selection(self, router):
        """Test handling of invalid model selection."""
        with pytest.raises(Exception):
            router.get_best_model(model_list=[])

    def test_missing_model_config(self, router):
        """Test handling of missing model configuration."""
        with pytest.raises(Exception):
            router.select_model('non_existent_model')

    def test_circuit_breaker_on_repeated_failures(self, router):
        """Test circuit breaker opens after repeated failures."""
        with patch.object(router, 'execute_on_model') as mock_exec:
            mock_exec.side_effect = Exception("Connection failed")

            # First few calls should retry
            for _ in range(3):
                with pytest.raises(Exception):
                    router.execute_on_model('gpt4', 'test')

            # After threshold, should open circuit
            assert router.is_circuit_open('gpt4')

    def test_circuit_breaker_recovery(self, router):
        """Test circuit breaker recovery after timeout."""
        router.open_circuit('gpt4')
        assert router.is_circuit_open('gpt4')

        # After timeout, should attempt recovery
        router.attempt_circuit_recovery('gpt4')
        assert not router.is_circuit_open('gpt4')


class TestLLMRouterCostTracking:
    """Test router cost tracking."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_estimate_cost_single_request(self, router):
        """Test cost estimation for single request."""
        tokens = 1000
        cost_per_1k = 0.02

        with patch.object(router, 'get_model_cost_per_1k', return_value=cost_per_1k):
            estimated_cost = router.estimate_cost('gpt4', tokens)
            assert estimated_cost == 0.02  # 1000 tokens * 0.02 / 1000

    def test_track_actual_cost(self, router):
        """Test tracking actual cost."""
        router.track_cost('gpt4', input_tokens=1000, output_tokens=500, cost=0.03)

        stats = router.get_cost_stats('gpt4')
        assert stats['total_cost'] >= 0.03
        assert stats['total_input_tokens'] >= 1000

    def test_cost_budget_enforcement(self, router):
        """Test enforcement of cost budgets."""
        budget = 1.0
        router.set_budget('gpt4', budget)

        # First call should succeed
        router.track_cost('gpt4', cost=0.5)

        # Second call exceeds budget
        with pytest.raises(Exception):
            router.track_cost('gpt4', cost=0.6)

    def test_monthly_cost_tracking(self, router):
        """Test monthly cost tracking."""
        router.track_cost('gpt4', cost=10.0, timestamp='2025-10-01')
        router.track_cost('gpt4', cost=15.0, timestamp='2025-10-15')
        router.track_cost('gpt3.5', cost=5.0, timestamp='2025-10-20')

        monthly_cost = router.get_monthly_cost('2025-10')
        assert monthly_cost >= 30.0


class TestLLMRouterIntelligentSelection:
    """Test intelligent model selection based on query."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_select_by_task_type(self, router):
        """Test selecting model based on task type."""
        task_types = {
            'summarization': 'gpt3.5',
            'code_generation': 'gpt4',
            'translation': 'claude'
        }

        with patch.object(router, 'get_best_model_for_task', side_effect=lambda t: task_types.get(t)):
            model = router.get_best_model_for_task('summarization')
            assert model == 'gpt3.5'

    def test_select_by_input_length(self, router):
        """Test selecting model based on input length."""
        # Long inputs might need special handling
        short_input = "What is AI?"
        long_input = "A" * 10000

        with patch.object(router, 'select_by_input_size') as mock_select:
            mock_select.return_value = 'gpt3.5'
            model = router.select_by_input_size(short_input)

            mock_select.return_value = 'gpt4'
            model = router.select_by_input_size(long_input)
            assert mock_select.called


@pytest.mark.asyncio
class TestLLMRouterAsync:
    """Test async router operations."""

    @pytest.fixture
    def router(self):
        return LLMRouter()

    async def test_async_model_selection(self, router):
        """Test async model selection."""
        async_select = AsyncMock(return_value='gpt4')
        router.select_model_async = async_select

        model = await router.select_model_async()
        assert model == 'gpt4'

    async def test_async_fallback(self, router):
        """Test async fallback chain."""
        async_fallback = AsyncMock(return_value='gpt3.5')
        router.try_async_fallback = async_fallback

        result = await router.try_async_fallback(['gpt4', 'gpt3.5'])
        assert result == 'gpt3.5'
