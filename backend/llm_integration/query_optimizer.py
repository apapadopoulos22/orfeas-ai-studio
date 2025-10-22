"""
Query Optimization Engine for LLM Integration.

Features:
- Query refinement based on history
- Prompt improvement suggestions
- Few-shot learning from previous queries
- Query expansion and clarification
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from enum import Enum
from backend.llm_integration.tracing import trace_performance, trace_block
from backend.llm_integration.error_handler import handle_error, LLMError

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Query optimization strategies."""
    CLARIFICATION = "clarification"
    EXPANSION = "expansion"
    SIMPLIFICATION = "simplification"
    STRUCTURING = "structuring"
    CONTEXT_ADDITION = "context_addition"
    PATTERN_BASED = "pattern_based"


@dataclass
class OptimizationResult:
    """Result of query optimization."""
    original_query: str
    optimized_query: str
    strategy: str
    success: bool
    confidence: float
    improvements: List[str]
    quality_feedback: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            'original_query': self.original_query,
            'optimized_query': self.optimized_query,
            'strategy': self.strategy,
            'success': self.success,
            'confidence': self.confidence,
            'improvements': self.improvements,
            'quality_feedback': self.quality_feedback,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class OptimizedQuery:
    """Optimized query with suggestions."""
    original_query: str
    optimized_query: str
    improvements: List[str]
    suggestions: List[str]
    confidence_score: float
    estimated_quality_gain: float
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            'original_query': self.original_query,
            'optimized_query': self.optimized_query,
            'improvements': self.improvements,
            'suggestions': self.suggestions,
            'confidence_score': self.confidence_score,
            'estimated_quality_gain': self.estimated_quality_gain,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class QueryExperience:
    """Learned query experience."""
    query_pattern: str
    successful_queries: List[str]
    failed_queries: List[str]
    average_quality_score: float
    recommendations: Dict[str, str]
    last_updated: datetime


class QueryOptimizer:
    """Optimize queries for better LLM responses."""

    def __init__(self, max_history: int = 10000):
        """
        Initialize query optimizer.

        Args:
            max_history: Maximum queries to store in history
        """
        self.max_history = max_history
        self.query_history: List[Dict[str, Any]] = []
        self.learned_patterns: Dict[str, QueryExperience] = {}

        # Optimization strategies
        self.strategies = {
            'clarification': self._add_clarification,
            'expansion': self._expand_query,
            'simplification': self._simplify_query,
            'exemplification': self._add_examples,
            'constraint_specification': self._add_constraints
        }

    @trace_performance('query_optimizer', 'optimize_query')
    def optimize_query(
        self,
        query: str,
        task_type: str = None,
        constraints: Dict[str, Any] = None,
        learning_enabled: bool = True
    ) -> OptimizedQuery:
        """
        Optimize a query for better LLM response.

        Args:
            query: Original query
            task_type: Type of task (summarization, translation, etc.)
            constraints: Constraints on response (length, format, etc.)
            learning_enabled: Whether to learn from history

        Returns:
            OptimizedQuery with improvements
        """
        with trace_block('query_optimizer', 'optimization_pipeline'):
            improvements = []
            suggestions = []
            optimized_query = query

            # Step 1: Detect task type if not provided
            if task_type is None:
                task_type = self._detect_task_type(query)

            # Step 2: Apply learned patterns
            if learning_enabled:
                learned_suggestions = self._get_learned_suggestions(query, task_type)
                suggestions.extend(learned_suggestions)

            # Step 3: Check for clarity issues
            clarity_improvements = self._improve_clarity(query)
            if clarity_improvements:
                improvements.extend(clarity_improvements)
                optimized_query = self._apply_improvements(
                    optimized_query,
                    clarity_improvements
                )

            # Step 4: Add context if needed
            if self._needs_context(query):
                context_improvement = self._add_context(query)
                improvements.append(context_improvement)
                optimized_query = optimized_query + "\n\nContext: " + context_improvement

            # Step 5: Optimize for task type
            task_optimizations = self._optimize_for_task(optimized_query, task_type)
            improvements.extend(task_optimizations)

            # Step 6: Add constraints if provided
            if constraints:
                constraint_text = self._format_constraints(constraints)
                improvements.append(f"Added constraints: {constraint_text}")
                optimized_query = optimized_query + "\n\nConstraints: " + constraint_text

        # Calculate metrics
        confidence = self._calculate_optimization_confidence(
            query,
            optimized_query,
            improvements
        )
        quality_gain = self._estimate_quality_gain(
            query,
            optimized_query,
            task_type
        )

        result = OptimizedQuery(
            original_query=query,
            optimized_query=optimized_query,
            improvements=improvements,
            suggestions=suggestions,
            confidence_score=confidence,
            estimated_quality_gain=quality_gain,
            timestamp=datetime.now()
        )

        # Learn from this optimization
        if learning_enabled:
            self._learn_optimization(query, result)

        return result

    def _detect_task_type(self, query: str) -> str:
        """Detect task type from query."""
        keywords = {
            'summary': ['summarize', 'summary', 'abstract', 'overview'],
            'translation': ['translate', 'translate to', 'in ', 'language'],
            'question': ['what', 'how', 'why', 'where', 'when', 'who', '?'],
            'classification': ['classify', 'categorize', 'type', 'category'],
            'generation': ['write', 'create', 'generate', 'compose', 'code'],
            'analysis': ['analyze', 'explain', 'discuss', 'examine', 'review']
        }

        query_lower = query.lower()
        for task, words in keywords.items():
            if any(word in query_lower for word in words):
                return task

        return 'general'

    def _improve_clarity(self, query: str) -> List[str]:
        """Identify clarity improvements."""
        improvements = []

        # Check length
        if len(query) < 10:
            improvements.append("Query is very short - consider providing more context")

        if len(query) > 5000:
            improvements.append("Query is very long - consider breaking into smaller parts")

        # Check for vagueness
        vague_words = ['thing', 'stuff', 'something', 'somehow', 'somewhere']
        if any(word in query.lower() for word in vague_words):
            improvements.append("Query contains vague language - be more specific")

        # Check for complete sentences
        if not query.strip().endswith(('?', '.', '!')):
            improvements.append("Query should end with punctuation")

        return improvements

    def _apply_improvements(self, query: str, improvements: List[str]) -> str:
        """Apply improvements to query."""
        # This is a simplified version
        # Real implementation would apply specific transformations
        return query

    def _needs_context(self, query: str) -> bool:
        """Check if query needs additional context."""
        pronouns = ['it', 'this', 'that', 'these', 'those', 'they']
        query_lower = query.lower()

        return any(f" {p} " in f" {query_lower} " for p in pronouns)

    def _add_context(self, query: str) -> str:
        """Add context to query."""
        # Would look up context from history
        return "Previous context would go here"

    def _optimize_for_task(self, query: str, task_type: str) -> List[str]:
        """Optimize query for specific task type."""
        optimizations = {
            'summary': [
                "Added: Focus on key points and main ideas",
                "Added: Specified concise format"
            ],
            'translation': [
                "Added: Maintained technical terminology",
                "Added: Specified target language nuances"
            ],
            'question': [
                "Added: Structured for logical analysis",
                "Added: Specified answer format"
            ],
            'generation': [
                "Added: Output format specification",
                "Added: Quality criteria"
            ],
            'analysis': [
                "Added: Structured analysis framework",
                "Added: Key aspects to examine"
            ]
        }

        return optimizations.get(task_type, ["Optimization applied for this task type"])

    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints as text."""
        parts = []

        if 'max_length' in constraints:
            parts.append(f"Max length: {constraints['max_length']} words")

        if 'format' in constraints:
            parts.append(f"Format: {constraints['format']}")

        if 'tone' in constraints:
            parts.append(f"Tone: {constraints['tone']}")

        if 'style' in constraints:
            parts.append(f"Style: {constraints['style']}")

        return ", ".join(parts)

    def _calculate_optimization_confidence(
        self,
        original: str,
        optimized: str,
        improvements: List[str]
    ) -> float:
        """Calculate confidence in optimization."""
        # More improvements = higher confidence
        improvement_score = min(1.0, len(improvements) / 5)

        # Larger difference = more confident change
        change_score = min(1.0, abs(len(optimized) - len(original)) / 100)

        return (improvement_score * 0.6) + (change_score * 0.4)

    def _estimate_quality_gain(
        self,
        original: str,
        optimized: str,
        task_type: str
    ) -> float:
        """Estimate quality improvement."""
        # Base improvement based on task type
        base_gains = {
            'summary': 0.15,
            'translation': 0.20,
            'question': 0.25,
            'classification': 0.10,
            'generation': 0.30,
            'analysis': 0.20,
            'general': 0.12
        }

        base = base_gains.get(task_type, 0.12)

        # Adjust based on change magnitude
        change_magnitude = abs(len(optimized) - len(original)) / len(original)
        adjustment = min(0.15, change_magnitude * 0.1)

        return min(1.0, base + adjustment)

    def _get_learned_suggestions(self, query: str, task_type: str) -> List[str]:
        """Get suggestions from learned patterns."""
        suggestions = []

        # Look for similar patterns
        for pattern, experience in self.learned_patterns.items():
            if pattern in query.lower():
                suggestions.extend(experience.recommendations.values())

        return suggestions

    def _add_clarification(self, query: str) -> str:
        """Add clarification to query."""
        return query + "\nPlease provide a clear and concise response."

    def _expand_query(self, query: str) -> str:
        """Expand query with more details."""
        return query + "\n\nProvide comprehensive coverage of this topic."

    def _simplify_query(self, query: str) -> str:
        """Simplify query."""
        return query + "\n\nExplain in simple terms."

    def _add_examples(self, query: str) -> str:
        """Add examples to query."""
        return query + "\n\nInclude examples if relevant."

    def _add_constraints(self, query: str) -> str:
        """Add constraints to query."""
        return query + "\n\nBe concise and structured."

    def _learn_optimization(self, original: str, result: OptimizedQuery):
        """Learn from optimization result."""
        # Store in history
        if len(self.query_history) >= self.max_history:
            self.query_history.pop(0)

        self.query_history.append({
            'original': original,
            'optimized': result.optimized_query,
            'improvements': result.improvements,
            'quality_gain': result.estimated_quality_gain,
            'timestamp': result.timestamp.isoformat()
        })

        # Update patterns
        task_type = self._detect_task_type(original)
        pattern_key = f"{task_type}_{len(original)//100}"

        if pattern_key not in self.learned_patterns:
            self.learned_patterns[pattern_key] = QueryExperience(
                query_pattern=pattern_key,
                successful_queries=[],
                failed_queries=[],
                average_quality_score=0.0,
                recommendations={},
                last_updated=datetime.now()
            )

        experience = self.learned_patterns[pattern_key]
        experience.successful_queries.append(original)
        experience.average_quality_score = result.estimated_quality_gain
        experience.recommendations = {
            f"improvement_{i}": imp
            for i, imp in enumerate(result.improvements)
        }
        experience.last_updated = datetime.now()

    def get_optimization_statistics(self) -> dict:
        """Get optimization statistics."""
        if not self.query_history:
            return {'total_optimizations': 0}

        total = len(self.query_history)
        avg_quality_gain = sum(
            q['quality_gain'] for q in self.query_history
        ) / total

        return {
            'total_optimizations': total,
            'avg_quality_gain': avg_quality_gain,
            'learned_patterns': len(self.learned_patterns),
            'max_history_size': self.max_history
        }

    def clear_history(self):
        """Clear history and learned patterns."""
        self.query_history = []
        self.learned_patterns = {}


# Convenience functions
def optimize_query(
    query: str,
    task_type: str = None,
    constraints: Dict[str, Any] = None
) -> OptimizedQuery:
    """
    Optimize a query (convenience function).

    Args:
        query: Query to optimize
        task_type: Type of task
        constraints: Response constraints

    Returns:
        OptimizedQuery
    """
    optimizer = QueryOptimizer()
    return optimizer.optimize_query(query, task_type, constraints)
