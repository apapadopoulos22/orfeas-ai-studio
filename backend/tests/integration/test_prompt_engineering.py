"""
Unit tests for prompt_engineering.py
"""

import pytest
import time
from backend.llm_integration.prompt_engineering import (
    PromptEngineer,
    PromptTemplate,
    PromptContext,
    OptimizedPrompt,
    get_prompt_engineer,
)


class TestPromptEngineer:
    """Test PromptEngineer functionality."""

    @pytest.fixture
    def engineer(self):
        """Create a PromptEngineer instance."""
        return PromptEngineer()

    def test_initialization(self, engineer):
        """Test PromptEngineer initialization."""
        assert engineer is not None
        assert engineer.optimization_stats['optimizations_performed'] == 0
        assert len(engineer.example_library) > 0

    def test_optimize_simple_prompt(self, engineer):
        """Test optimization of a simple prompt."""
        prompt = "write hello world"
        result = engineer.optimize_prompt(prompt)

        assert isinstance(result, OptimizedPrompt)
        assert result.original_prompt == prompt
        assert len(result.optimized_prompt) > 0
        assert result.optimization_time_ms < 100  # Target: <100ms
        assert result.confidence_score > 0.5

    def test_clean_prompt(self, engineer):
        """Test prompt cleaning."""
        prompt = "write    a    function   teh  sum"
        result = engineer.optimize_prompt(prompt)

        # Should have cleaned whitespace and fixed typo
        assert "    " not in result.optimized_prompt
        assert "teh" not in result.optimized_prompt.lower()

    def test_add_structure(self, engineer):
        """Test structure addition."""
        prompt = "list all the items"
        result = engineer.optimize_prompt(prompt)

        assert "structure" in result.enhancements_applied
        assert len(result.optimized_prompt) > len(prompt)

    def test_chain_of_thought_for_complex(self, engineer):
        """Test chain-of-thought for complex tasks."""
        context = PromptContext(
            task_type="reasoning",
            complexity_level="complex",
            domain="logic",
        )
        prompt = "Solve this puzzle"
        result = engineer.optimize_prompt(prompt, context)

        assert "chain_of_thought" in result.enhancements_applied
        assert "step" in result.optimized_prompt.lower()

    def test_few_shot_examples_code(self, engineer):
        """Test few-shot example injection for code generation."""
        context = PromptContext(
            task_type="code_generation",
            complexity_level="moderate",
            domain="programming",
            examples_needed=True,
        )
        prompt = "Write a sorting function"
        result = engineer.optimize_prompt(prompt, context=context, include_examples=True)

        assert "few_shot_examples" in result.enhancements_applied
        assert "Example" in result.optimized_prompt

    def test_token_estimation(self, engineer):
        """Test token estimation."""
        prompt = "This is a test prompt with ten words in it"
        result = engineer.optimize_prompt(prompt)

        # Should estimate reasonable number of tokens
        assert result.estimated_tokens > 0
        assert result.estimated_tokens < len(prompt)

    def test_output_format_addition(self, engineer):
        """Test output format guidance."""
        context = PromptContext(
            task_type="analysis",
            complexity_level="simple",
            domain="text",
            output_format="JSON",
        )
        prompt = "Analyze this text"
        result = engineer.optimize_prompt(prompt, context=context)

        assert "output_format" in result.enhancements_applied
        assert "JSON" in result.optimized_prompt

    def test_batch_optimize(self, engineer):
        """Test batch optimization."""
        prompts = [
            "write code",
            "analyze text",
            "solve problem",
        ]
        results = engineer.batch_optimize(prompts)

        assert len(results) == 3
        assert all(isinstance(r, OptimizedPrompt) for r in results)
        assert engineer.optimization_stats['optimizations_performed'] == 3

    def test_optimization_statistics(self, engineer):
        """Test optimization statistics tracking."""
        prompt1 = "write a function"
        prompt2 = "analyze this"

        engineer.optimize_prompt(prompt1)
        engineer.optimize_prompt(prompt2)

        stats = engineer.get_optimization_stats()
        assert stats['total_optimizations'] == 2
        assert stats['avg_time_ms'] < 100
        assert len(stats['enhancements_applied']) > 0

    def test_confidence_score_calculation(self, engineer):
        """Test confidence score calculation."""
        context = PromptContext(
            task_type="code",
            complexity_level="complex",
            domain="python",
        )
        prompt = "Write a function"
        result = engineer.optimize_prompt(prompt, context=context)

        # Complex with context should have higher confidence
        assert result.confidence_score > 0.7
        assert result.confidence_score <= 0.95

    def test_reset_statistics(self, engineer):
        """Test statistics reset."""
        engineer.optimize_prompt("test prompt 1")
        engineer.optimize_prompt("test prompt 2")

        assert engineer.optimization_stats['optimizations_performed'] == 2

        engineer.reset_stats()

        assert engineer.optimization_stats['optimizations_performed'] == 0
        assert engineer.optimization_stats['avg_optimization_time_ms'] == 0.0

    def test_get_prompt_engineer_singleton(self):
        """Test get_prompt_engineer returns singleton."""
        engineer1 = get_prompt_engineer()
        engineer2 = get_prompt_engineer()

        assert engineer1 is engineer2

    def test_optimization_time_reasonable(self, engineer):
        """Test optimization completes in reasonable time."""
        start = time.time()
        engineer.optimize_prompt("write a long prompt with many words to test performance and timing")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert duration < 100  # Should be under 100ms


class TestPromptContext:
    """Test PromptContext dataclass."""

    def test_context_creation(self):
        """Test PromptContext creation."""
        context = PromptContext(
            task_type="code_generation",
            complexity_level="complex",
            domain="python",
        )

        assert context.task_type == "code_generation"
        assert context.complexity_level == "complex"
        assert context.domain == "python"
        assert context.examples_needed == False
        assert context.max_tokens == 2048

    def test_context_with_optional_fields(self):
        """Test PromptContext with optional fields."""
        context = PromptContext(
            task_type="analysis",
            complexity_level="simple",
            domain="text",
            output_format="markdown",
            examples_needed=True,
            max_tokens=1024,
        )

        assert context.output_format == "markdown"
        assert context.examples_needed == True
        assert context.max_tokens == 1024


class TestOptimizedPrompt:
    """Test OptimizedPrompt dataclass."""

    def test_optimized_prompt_creation(self):
        """Test OptimizedPrompt creation."""
        result = OptimizedPrompt(
            original_prompt="test",
            optimized_prompt="test optimized",
            enhancements_applied=["cleaned", "structured"],
            estimated_tokens=10,
            optimization_time_ms=25.5,
            confidence_score=0.85,
        )

        assert result.original_prompt == "test"
        assert result.optimized_prompt == "test optimized"
        assert len(result.enhancements_applied) == 2
        assert result.estimated_tokens == 10
        assert result.confidence_score == 0.85


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
