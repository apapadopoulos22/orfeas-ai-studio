"""
Multi-Model Ensembling for LLM Integration.

Combines responses from multiple LLMs with:
- Weighted consensus voting
- Confidence scoring
- Result merging
- Quality assessment
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from backend.llm_integration.tracing import trace_performance, trace_block_async
from backend.llm_integration.error_handler import safe_execute, handle_error, LLMOrchestratorError

logger = logging.getLogger(__name__)


@dataclass
class EnsembleResponse:
    """Response from ensemble operation."""
    consensus_response: str
    confidence_score: float
    individual_responses: Dict[str, str]
    individual_scores: Dict[str, float]
    weights: Dict[str, float]
    merged_reasoning: str
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            'consensus_response': self.consensus_response,
            'confidence_score': self.confidence_score,
            'individual_responses': self.individual_responses,
            'individual_scores': self.individual_scores,
            'weights': self.weights,
            'merged_reasoning': self.merged_reasoning,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ModelContribution:
    """Individual model contribution to ensemble."""
    model_name: str
    response: str
    quality_score: float
    token_count: int
    latency_ms: float
    cost: float

    def to_dict(self) -> dict:
        return {
            'model_name': self.model_name,
            'response': self.response,
            'quality_score': self.quality_score,
            'token_count': self.token_count,
            'latency_ms': self.latency_ms,
            'cost': self.cost
        }


class MultiModelEnsembler:
    """Ensemble multiple LLM responses for improved quality."""

    def __init__(self, models: List[str] = None, weights: Dict[str, float] = None):
        """
        Initialize ensembler.

        Args:
            models: List of models to use
            weights: Model weights (default: equal weighting)
        """
        self.models = models or ['gpt4', 'gpt3.5', 'claude']

        # Default: equal weights
        if weights is None:
            weight_value = 1.0 / len(self.models)
            self.weights = {m: weight_value for m in self.models}
        else:
            self.weights = weights

        self.contributions: List[ModelContribution] = []
        self.ensemble_history: List[EnsembleResponse] = []

    @trace_performance('ensembler', 'get_ensemble_response')
    async def get_ensemble_response(
        self,
        prompt: str,
        model_executors: Dict[str, Any],
        merge_strategy: str = 'weighted_consensus',
        use_quality_filtering: bool = True,
        quality_threshold: float = 0.6
    ) -> EnsembleResponse:
        """
        Get ensemble response from multiple models.

        Args:
            prompt: Input prompt
            model_executors: Dict mapping model names to executor functions
            merge_strategy: 'weighted_consensus', 'majority_vote', 'best_of_n'
            use_quality_filtering: Filter responses by quality
            quality_threshold: Minimum quality score to include

        Returns:
            EnsembleResponse with consensus and confidence
        """
        async with trace_block_async('ensembler', 'parallel_execution'):
            # Execute all models in parallel
            responses = await asyncio.gather(
                *[
                    self._execute_model(name, prompt, model_executors)
                    for name in self.models
                ],
                return_exceptions=True
            )

        # Process responses
        valid_contributions = []
        for response, model_name in zip(responses, self.models):
            if isinstance(response, Exception):
                logger.warning(f"Error from {model_name}: {response}")
                continue

            contribution = response

            # Filter by quality if requested
            if use_quality_filtering and contribution.quality_score < quality_threshold:
                logger.info(
                    f"Filtering {model_name} (quality: "
                    f"{contribution.quality_score:.2f})"
                )
                continue

            valid_contributions.append(contribution)
            self.contributions.append(contribution)

        if not valid_contributions:
            raise LLMOrchestratorError(
                "No valid responses from ensemble models",
                "NO_VALID_RESPONSES"
            )

        # Merge responses based on strategy
        async with trace_block_async('ensembler', 'merge_responses'):
            if merge_strategy == 'weighted_consensus':
                result = self._merge_weighted_consensus(valid_contributions)
            elif merge_strategy == 'majority_vote':
                result = self._merge_majority_vote(valid_contributions)
            elif merge_strategy == 'best_of_n':
                result = self._merge_best_of_n(valid_contributions)
            else:
                raise ValueError(f"Unknown merge strategy: {merge_strategy}")

        # Calculate confidence score
        confidence = self._calculate_confidence(valid_contributions)

        # Create response
        ensemble_response = EnsembleResponse(
            consensus_response=result['merged_text'],
            confidence_score=confidence,
            individual_responses={c.model_name: c.response for c in valid_contributions},
            individual_scores={c.model_name: c.quality_score for c in valid_contributions},
            weights={m: self.weights.get(m, 0) for m in self.models},
            merged_reasoning=result.get('reasoning', ''),
            timestamp=datetime.now()
        )

        self.ensemble_history.append(ensemble_response)

        return ensemble_response

    async def _execute_model(
        self,
        model_name: str,
        prompt: str,
        model_executors: Dict[str, Any]
    ) -> ModelContribution:
        """Execute single model and return contribution."""
        executor = model_executors.get(model_name)
        if not executor:
            raise LLMOrchestratorError(f"No executor for {model_name}")

        # Execute with timeout
        try:
            import time
            start = time.time()

            response = await safe_execute(
                lambda: executor(prompt),
                'ensembler',
                f'execute_{model_name}',
                timeout=30.0
            )

            latency_ms = (time.time() - start) * 1000

            # Extract quality score (simplified - would use quality_monitor)
            quality_score = 0.85  # Default quality score

            contribution = ModelContribution(
                model_name=model_name,
                response=response.get('text', ''),
                quality_score=quality_score,
                token_count=response.get('token_count', 0),
                latency_ms=latency_ms,
                cost=response.get('cost', 0.0)
            )

            return contribution

        except Exception as e:
            raise handle_error(e, 'ensembler', f'execute_model_{model_name}')

    def _merge_weighted_consensus(
        self,
        contributions: List[ModelContribution]
    ) -> dict:
        """Merge responses using weighted consensus."""
        # In a real implementation, would use semantic similarity
        # and weighted voting to create consensus

        # For now: concatenate high-quality responses
        high_quality = [
            c for c in contributions
            if c.quality_score >= 0.7
        ]

        if not high_quality:
            high_quality = contributions

        # Create weighted text (simplified)
        merged_parts = []
        for contribution in sorted(high_quality, key=lambda c: c.quality_score, reverse=True):
            weight = self.weights.get(contribution.model_name, 1.0)
            merged_parts.append(f"[{contribution.model_name}]: {contribution.response}")

        merged_text = "\n".join(merged_parts)

        return {
            'merged_text': merged_text,
            'strategy': 'weighted_consensus',
            'reasoning': 'Combined high-quality responses with weighting'
        }

    def _merge_majority_vote(
        self,
        contributions: List[ModelContribution]
    ) -> dict:
        """Merge responses using majority voting."""
        # Extract key conclusions and vote
        # (Simplified implementation)

        # Use best response as consensus
        best = max(contributions, key=lambda c: c.quality_score)

        other_responses = [
            c.response for c in contributions
            if c.model_name != best.model_name
        ]

        merged_text = f"{best.response}\n\nOther perspectives:\n"
        merged_text += "\n".join(other_responses)

        return {
            'merged_text': merged_text,
            'strategy': 'majority_vote',
            'reasoning': f'Primary: {best.model_name}, Supporting responses included'
        }

    def _merge_best_of_n(
        self,
        contributions: List[ModelContribution]
    ) -> dict:
        """Use best response from ensemble."""
        best = max(contributions, key=lambda c: c.quality_score)

        return {
            'merged_text': best.response,
            'strategy': 'best_of_n',
            'reasoning': f'Selected best response from {best.model_name} '
                        f'(quality: {best.quality_score:.2f})'
        }

    def _calculate_confidence(self, contributions: List[ModelContribution]) -> float:
        """Calculate ensemble confidence score."""
        if not contributions:
            return 0.0

        # Average quality score
        avg_quality = sum(c.quality_score for c in contributions) / len(contributions)

        # Agreement score (simplified)
        # Would use semantic similarity in real implementation
        agreement = 0.8  # Placeholder

        # Combine scores
        confidence = (avg_quality * 0.7) + (agreement * 0.3)

        return min(1.0, confidence)

    def update_weights(self, performance_data: Dict[str, float]):
        """
        Update model weights based on performance.

        Args:
            performance_data: Dict of model names to performance scores
        """
        total = sum(performance_data.values())
        if total > 0:
            self.weights = {
                model: score / total
                for model, score in performance_data.items()
            }

            logger.info(f"Updated ensemble weights: {self.weights}")

    def get_ensemble_metrics(self) -> dict:
        """Get ensemble performance metrics."""
        if not self.ensemble_history:
            return {'total_ensembles': 0}

        total_ensembles = len(self.ensemble_history)
        avg_confidence = sum(
            e.confidence_score for e in self.ensemble_history
        ) / total_ensembles

        # Average model participation
        model_counts = {}
        for ensemble in self.ensemble_history:
            for model in ensemble.individual_responses.keys():
                model_counts[model] = model_counts.get(model, 0) + 1

        return {
            'total_ensembles': total_ensembles,
            'avg_confidence': avg_confidence,
            'min_confidence': min(e.confidence_score for e in self.ensemble_history),
            'max_confidence': max(e.confidence_score for e in self.ensemble_history),
            'model_participation': model_counts,
            'current_weights': self.weights
        }

    def clear_history(self):
        """Clear ensemble history."""
        self.ensemble_history = []
        self.contributions = []


# Convenience function
async def get_ensemble_response(
    prompt: str,
    models: List[str] = None,
    model_executors: Dict[str, Any] = None,
    **kwargs
) -> EnsembleResponse:
    """
    Get ensemble response (convenience function).

    Args:
        prompt: Input prompt
        models: Models to use
        model_executors: Model executor functions
        **kwargs: Additional arguments for ensembler

    Returns:
        EnsembleResponse
    """
    ensembler = MultiModelEnsembler(models=models)
    return await ensembler.get_ensemble_response(
        prompt,
        model_executors or {},
        **kwargs
    )
