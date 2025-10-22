"""
Prompt Engineering Module - Dynamic Prompt Optimization

Purpose:
    Dynamically optimize prompts for better LLM results through:
    - Structured prompt formatting
    - Few-shot example injection
    - Context-aware enhancement
    - Model-specific adaptation
    - Token counting integration

Performance Targets:
    - Prompt optimization: <50ms
    - Example selection: <30ms
    - Context injection: <20ms
    - Total per-request: <100ms
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from .error_handler import (
    error_context,
    safe_execute,
    PromptEngineeringError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)
from .query_optimizer import (
    QueryOptimizer,
    OptimizationStrategy,
    OptimizationResult
)

logger = logging.getLogger(__name__)


class PromptTemplate(Enum):
    """Pre-defined prompt templates for common tasks."""
    SIMPLE = "simple"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"
    ROLE_BASED = "role_based"
    STRUCTURED = "structured"


@dataclass
class PromptContext:
    """Context information for prompt optimization."""
    task_type: str
    complexity_level: str  # simple, moderate, complex
    domain: str
    output_format: Optional[str] = None
    examples_needed: bool = False
    max_tokens: int = 2048


@dataclass
class OptimizedPrompt:
    """Result of prompt optimization."""
    original_prompt: str
    optimized_prompt: str
    enhancements_applied: List[str]
    estimated_tokens: int
    optimization_time_ms: float
    confidence_score: float  # 0.0-1.0


class PromptEngineer:
    """
    Dynamic prompt optimization system.

    Improves LLM performance through intelligent prompt engineering.
    """

    def __init__(self):
        """Initialize the prompt engineer."""
        self.optimization_stats = {
            'optimizations_performed': 0,
            'avg_optimization_time_ms': 0.0,
            'enhancements_applied': {},
        }
        self.example_library = self._initialize_examples()
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        self.query_optimizer = QueryOptimizer()
        self.auto_optimization_enabled = True
        logger.info("PromptEngineer initialized")

    def _initialize_examples(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize example library for few-shot learning."""
        return {
            'code_generation': [
                {
                    'input': 'Write a Python function to calculate factorial',
                    'output': '''def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)'''
                },
                {
                    'input': 'Create a function to merge two sorted arrays',
                    'output': '''def merge_sorted(arr1: list, arr2: list) -> list:
    """Merge two sorted arrays."""
    result = []
    i = j = 0
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1
    result.extend(arr1[i:] + arr2[j:])
    return result'''
                },
            ],
            'analysis': [
                {
                    'input': 'Analyze the sentiment of: "I love this product!"',
                    'output': 'Sentiment: Positive | Confidence: 95% | Key terms: love'
                },
                {
                    'input': 'Analyze the sentiment of: "Terrible experience"',
                    'output': 'Sentiment: Negative | Confidence: 90% | Key terms: terrible'
                },
            ],
            'reasoning': [
                {
                    'input': 'If all dogs are animals and Fido is a dog, what can we conclude?',
                    'output': '''Step 1: All dogs are animals (given)
Step 2: Fido is a dog (given)
Step 3: Therefore, Fido is an animal (by logical deduction)
Conclusion: Fido must be an animal'''
                },
            ],
        }

    @trace_performance(operation='optimize_prompt', component='prompt_engineering')
    @error_context(component='prompt_engineering', operation='optimize_prompt')
    @trace_performance
    def optimize_prompt(
        self,
        prompt: str,
        context: Optional[PromptContext] = None,
        include_examples: bool = False,
    ) -> OptimizedPrompt:
        """
        Optimize a prompt for better LLM results.

        Args:
            prompt: The original user prompt
            context: Context information for optimization
            include_examples: Whether to include few-shot examples

        Returns:
            OptimizedPrompt with improvements applied
        """
        start_time = time.time()
        enhancements = []

        # Start with the original prompt
        optimized = prompt.strip()

        # Apply query optimizer auto-optimization if enabled
        if self.auto_optimization_enabled:
            try:
                optimization_result = self.query_optimizer.optimize_query(
                    optimized,
                    task_type=context.task_type if context else 'general',
                    quality_feedback=None
                )
                if optimization_result and optimization_result.success:
                    optimized = optimization_result.optimized_query
                    enhancements.append("auto_optimized")
                    logger.debug(f"Query optimizer applied: {optimization_result.strategy}")
            except Exception as e:
                logger.warning(f"Query optimizer failed: {e}")
                # Continue with standard optimization

        # Apply enhancements
        optimized = self._clean_prompt(optimized)
        if optimized != prompt:
            enhancements.append("cleaned")

        optimized = self._add_clarity(optimized)
        if len(optimized) > len(prompt):
            enhancements.append("clarity")

        optimized = self._add_structure(optimized)
        enhancements.append("structured")

        if context and context.examples_needed and include_examples:
            examples = self._select_examples(context)
            if examples:
                optimized = self._inject_examples(optimized, examples)
                enhancements.append("few_shot_examples")

        # Add output format guidance if specified
        if context and context.output_format:
            optimized = self._add_output_format(optimized, context.output_format)
            enhancements.append("output_format")

        # Apply chain-of-thought if complex task
        if context and context.complexity_level == 'complex':
            optimized = self._apply_chain_of_thought(optimized)
            enhancements.append("chain_of_thought")

        # Estimate tokens
        estimated_tokens = self._estimate_tokens(optimized)

        # Calculate metrics
        optimization_time = (time.time() - start_time) * 1000  # Convert to ms
        confidence = self._calculate_confidence(enhancements, context)

        # Update statistics
        self._update_stats(optimization_time, enhancements)

        logger.info(
            f"Optimized prompt with {len(enhancements)} enhancements "
            f"(time: {optimization_time:.2f}ms, tokens: {estimated_tokens})"
        )

        return OptimizedPrompt(
            original_prompt=prompt,
            optimized_prompt=optimized,
            enhancements_applied=enhancements,
            estimated_tokens=estimated_tokens,
            optimization_time_ms=optimization_time,
            confidence_score=confidence,
        )

    def _clean_prompt(self, prompt: str) -> str:
        """Clean prompt of unnecessary whitespace and formatting."""
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt)
        # Remove trailing/leading whitespace
        prompt = prompt.strip()
        # Fix common typos
        prompt = prompt.replace('teh ', 'the ')
        prompt = prompt.replace('recieve', 'receive')
        return prompt

    def _add_clarity(self, prompt: str) -> str:
        """Add clarity to the prompt."""
        # Check if prompt is vague and add specificity
        vague_terms = {
            'thing': 'concept',
            'stuff': 'items',
            'good': 'beneficial or positive',
            'bad': 'harmful or negative',
        }

        improved = prompt
        for vague, specific in vague_terms.items():
            if vague in improved.lower():
                improved = re.sub(
                    rf'\b{vague}\b',
                    specific,
                    improved,
                    flags=re.IGNORECASE
                )

        return improved

    def _add_structure(self, prompt: str) -> str:
        """Add structural guidance to the prompt."""
        # Check if this looks like a request that would benefit from structure
        if any(word in prompt.lower() for word in ['list', 'summarize', 'explain', 'analyze']):
            if not any(marker in prompt for marker in ['1.', '-', '*', '•']):
                prompt += "\n\nPlease structure your response with clear sections."

        return prompt
    @trace_performance(operation='select_examples', component='prompt_engineering')
    @error_context(component='prompt_engineering', operation='select_examples')
    @trace_performance
    def _select_examples(self, context: PromptContext) -> List[Dict[str, str]]:
        """Select relevant examples for few-shot learning."""
        # Map task type to example category
        task_to_category = {
            'code': 'code_generation',
            'analysis': 'analysis',
            'sentiment': 'analysis',
            'reasoning': 'reasoning',
            'logic': 'reasoning',
        }

        # Find matching category
        category = None
        for task_keyword, cat in task_to_category.items():
            if task_keyword in context.task_type.lower():
                category = cat
                break

        if category and category in self.example_library:
            # Return up to 2 relevant examples
            return self.example_library[category][:2]

        return []
    @trace_performance(operation='inject_examples', component='prompt_engineering')
    @trace_performance
    @error_context(component='prompt_engineering', operation='inject_examples')
    def _inject_examples(
        self,
        prompt: str,
        examples: List[Dict[str, str]]
    ) -> str:
        """Inject few-shot examples into the prompt."""
        if not examples:
            return prompt

        examples_text = "\n\nHere are some examples:\n"
        for i, example in enumerate(examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Input: {example['input']}\n"
            examples_text += f"Output: {example['output']}"

        examples_text += "\n\nNow, please:"
        return prompt + examples_text

    def _add_output_format(self, prompt: str, output_format: str) -> str:
        """Add output format guidance."""
        format_guidance = f"\n\nPlease format your response as: {output_format}"
        return prompt + format_guidance
    @trace_performance
    def _apply_chain_of_thought(self, prompt: str) -> str:
        """Apply chain-of-thought reasoning approach."""
        cot_guidance = (
            "\n\nPlease break down your reasoning step by step:\n"
            "1. First, understand the problem\n"
            "2. Think through the solution\n"
            "3. Provide your answer\n"
            "4. Explain your reasoning"
        )
        return prompt + cot_guidance

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).

        Rule of thumb: ~4 chars ≈ 1 token for English text
        """
        # More accurate estimation: average ~3-4 chars per token
        chars_per_token = 3.5
        return max(1, int(len(text) / chars_per_token))

    def _calculate_confidence(
        self,
        enhancements: List[str],
        context: Optional[PromptContext]
    ) -> float:
        """Calculate confidence in optimization."""
        base_confidence = 0.6

        # Add confidence for each enhancement
        confidence = base_confidence + (len(enhancements) * 0.05)

        # Adjust based on context
        if context:
            if context.complexity_level == 'complex':
                confidence += 0.1  # More confidence for complex prompts
            if context.domain:
                confidence += 0.05  # More confidence with domain context

        # Cap at 0.95
        return min(0.95, confidence)

    def _update_stats(self, optimization_time: float, enhancements: List[str]) -> None:
        """Update optimization statistics."""
        stats = self.optimization_stats

        stats['optimizations_performed'] += 1

        # Update average optimization time
        old_avg = stats['avg_optimization_time_ms']
        count = stats['optimizations_performed']
        new_avg = (old_avg * (count - 1) + optimization_time) / count
        stats['avg_optimization_time_ms'] = new_avg

        # Track enhancements applied
        for enhancement in enhancements:
            stats['enhancements_applied'][enhancement] = (
                stats['enhancements_applied'].get(enhancement, 0) + 1
            )

    def batch_optimize(
        self,
        prompts: List[str],
        context: Optional[PromptContext] = None,
    ) -> List[OptimizedPrompt]:
        """
        Optimize multiple prompts in batch.

        Args:
            prompts: List of prompts to optimize
            context: Optional context for all prompts

        Returns:
            List of OptimizedPrompt results
        """
        results = []
        for prompt in prompts:
            result = self.optimize_prompt(prompt, context)
            results.append(result)

        logger.info(f"Batch optimized {len(prompts)} prompts")
        return results

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        return {
            'total_optimizations': self.optimization_stats['optimizations_performed'],
            'avg_time_ms': self.optimization_stats['avg_optimization_time_ms'],
            'enhancements_applied': self.optimization_stats['enhancements_applied'].copy(),
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.optimization_stats = {
            'optimizations_performed': 0,
            'avg_optimization_time_ms': 0.0,
            'enhancements_applied': {},
        }
        logger.info("Optimization statistics reset")

    def configure_optimizer(
        self,
        auto_optimization_enabled: bool = True,
        merge_strategy: str = 'weighted_consensus'
    ) -> None:
        """Configure query optimizer settings."""
        self.auto_optimization_enabled = auto_optimization_enabled
        if hasattr(self.query_optimizer, 'merge_strategy'):
            self.query_optimizer.merge_strategy = merge_strategy
        logger.info(
            f"Query optimizer configured: "
            f"auto_optimization={auto_optimization_enabled}, "
            f"merge_strategy={merge_strategy}"
        )

    def provide_quality_feedback(
        self,
        query: str,
        quality_score: float,
        task_type: Optional[str] = None
    ) -> None:
        """Provide quality feedback for query optimization learning."""
        if hasattr(self.query_optimizer, 'record_quality'):
            try:
                self.query_optimizer.record_quality(
                    query=query,
                    quality_score=quality_score,
                    task_type=task_type or 'general'
                )
                logger.debug(
                    f"Quality feedback recorded: query={query[:50]}..., "
                    f"score={quality_score:.2f}"
                )
            except Exception as e:
                logger.warning(f"Failed to record quality feedback: {e}")

    def get_optimizer_status(self) -> Dict[str, Any]:
        """Get query optimizer status and metrics."""
        status = {
            'auto_optimization_enabled': self.auto_optimization_enabled,
            'optimizer_active': True,
        }
        if hasattr(self.query_optimizer, 'get_statistics'):
            try:
                status['optimizer_metrics'] = self.query_optimizer.get_statistics()
            except Exception as e:
                logger.warning(f"Failed to get optimizer metrics: {e}")
        return status


# Factory function for easy access
def get_prompt_engineer() -> PromptEngineer:
    """Get or create a PromptEngineer instance."""
    if not hasattr(get_prompt_engineer, '_instance'):
        get_prompt_engineer._instance = PromptEngineer()
    return get_prompt_engineer._instance

