"""
LLM Quality Monitor Module - Quality Assurance and Monitoring

Purpose:
    Monitor and validate LLM response quality:
    - Hallucination detection
    - Response quality scoring
    - Code validation for programming tasks
    - Toxicity and safety checking
    - Performance metrics and anomaly detection

Performance Targets:
    - Quality scoring: <50ms
    - Hallucination check: <100ms
    - Code validation: <100ms
    - Safety check: <50ms
    - Total per-response: <300ms
"""

import logging
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .error_handler import (
    error_context,
    safe_execute,
    QualityCheckError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Response quality levels."""
    EXCELLENT = 5  # 0.9-1.0
    GOOD = 4       # 0.7-0.9
    ACCEPTABLE = 3 # 0.5-0.7
    POOR = 2       # 0.3-0.5
    CRITICAL = 1   # 0.0-0.3


@dataclass
class QualityScore:
    """Quality assessment for a response."""
    overall_score: float  # 0.0-1.0
    quality_level: QualityLevel
    accuracy_score: float  # 0.0-1.0
    consistency_score: float  # 0.0-1.0
    clarity_score: float  # 0.0-1.0
    safety_score: float  # 0.0-1.0
    hallucination_risk: float  # 0.0-1.0 (0=low risk, 1=high risk)
    is_safe: bool
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class LLMQualityMonitor:
    """
    LLM response quality monitoring system.

    Validates response quality, detects hallucinations, and checks safety.
    """

    # Common hallucination indicators
    HALLUCINATION_PATTERNS = [
        r'\b(?:I\s+)?(?:have|has)\s+(?:no|not any)\s+(?:information|knowledge|data)\b',
        r'\bI\s+apologize\b',
        r'\b(?:as of|last updated|last checked)\s+\d{4}\b',
        r'\b(?:I\s+)?cannot\s+verify\b',
        r'\b(?:according to|based on)\s+(?:my|the)\s+(?:knowledge|training)\b',
    ]

    # Safety keywords (toxic, hateful, violent content)
    SAFETY_KEYWORDS = {
        'toxic': ['hate', 'kill', 'violence', 'abuse', 'assault'],
        'harmful': ['poison', 'bomb', 'weapon', 'exploit'],
        'inappropriate': ['slur', 'offensive', 'discriminate'],
    }

    def __init__(self):
        """Initialize quality monitor."""
        self.quality_history: List[QualityScore] = []
        self.stats = {
            'responses_evaluated': 0,
            'avg_quality_score': 0.0,
            'hallucination_detections': 0,
            'safety_issues': 0,
        }
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        logger.info("LLMQualityMonitor initialized")

    @trace_performance(operation='evaluate_response', component='llm_quality_monitor')
    @error_context(component='llm_quality_monitor', operation='evaluate_response')
    def evaluate_response(
        self,
        response: str,
        context: Optional[str] = None,
        ground_truth: Optional[str] = None,
        task_type: str = "general",
    ) -> QualityScore:
        """
        Evaluate overall quality of LLM response.

        Args:
            response: The LLM response to evaluate
            context: Original query context
            ground_truth: Expected/reference answer (optional)
            task_type: Type of task (general, code, factual, creative)

        Returns:
            QualityScore with detailed assessment
        """
        # Calculate individual scores
        accuracy = self._calculate_accuracy(response, ground_truth) if ground_truth else 0.7
        consistency = self._calculate_consistency(response)
        clarity = self._calculate_clarity(response)
        safety = self._calculate_safety(response)
        hallucination_risk = self._detect_hallucination_risk(response)

        # Weighted average based on task type
        if task_type == "code":
            weights = {'accuracy': 0.35, 'consistency': 0.2, 'clarity': 0.15, 'safety': 0.3}
        elif task_type == "factual":
            weights = {'accuracy': 0.4, 'consistency': 0.25, 'clarity': 0.15, 'safety': 0.2}
        else:  # general
            weights = {'accuracy': 0.25, 'consistency': 0.25, 'clarity': 0.3, 'safety': 0.2}

        # Apply hallucination penalty
        overall_score = (
            accuracy * weights['accuracy'] +
            consistency * weights['consistency'] +
            clarity * weights['clarity'] +
            safety * weights['safety']
        )
        overall_score *= (1.0 - hallucination_risk * 0.3)  # Hallucination penalty

        # Clamp to 0-1
        overall_score = max(0.0, min(1.0, overall_score))

        # Determine quality level
        if overall_score >= 0.9:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 0.7:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 0.5:
            quality_level = QualityLevel.ACCEPTABLE
        elif overall_score >= 0.3:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.CRITICAL

        # Check for issues
        warnings = []
        if hallucination_risk > 0.5:
            warnings.append(f"High hallucination risk: {hallucination_risk:.1%}")
        if safety < 0.8:
            warnings.append("Safety concerns detected")
        if clarity < 0.6:
            warnings.append("Response lacks clarity")

        is_safe = safety > 0.7

        # Create score object
        score = QualityScore(
            overall_score=overall_score,
            quality_level=quality_level,
            accuracy_score=accuracy,
            consistency_score=consistency,
            clarity_score=clarity,
            safety_score=safety,
            hallucination_risk=hallucination_risk,
            is_safe=is_safe,
            warnings=warnings,
        )

        # Track
        self._track_score(score)

        logger.info(
            f"Response evaluated: quality={overall_score:.2f}, "
            f"hallucination_risk={hallucination_risk:.2f}, "
            f"safe={is_safe}"
        )

        return score

    def _calculate_accuracy(self, response: str, ground_truth: str) -> float:
        """Calculate accuracy by comparing with ground truth."""
        if not response or not ground_truth:
            return 0.5

        # Simple word overlap similarity
        response_words = set(response.lower().split())
        truth_words = set(ground_truth.lower().split())

        if not truth_words:
            return 0.5

        intersection = len(response_words & truth_words)
        similarity = intersection / len(truth_words)

        return min(1.0, similarity)

    def _calculate_consistency(self, response: str) -> float:
        """Check for internal consistency in response."""
        # Look for contradictions
        contradictions = 0
        contradiction_pairs = [
            (r'\balways\b', r'\bnever\b'),
            (r'\bcertain\b', r'\buncertain\b'),
            (r'\byes\b', r'\bno\b'),
        ]

        for pos, neg in contradiction_pairs:
            if re.search(pos, response, re.IGNORECASE) and \
               re.search(neg, response, re.IGNORECASE):
                contradictions += 1

        # Check for repeated sentences (padding indicator)
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        unique_sentences = set(sentences)
        repetition_ratio = 1.0 - (len(unique_sentences) / max(1, len(sentences)))

        consistency_score = 1.0 - (contradictions * 0.2 + repetition_ratio * 0.3)

        return max(0.0, min(1.0, consistency_score))

    def _calculate_clarity(self, response: str) -> float:
        """Evaluate response clarity and structure."""
        if not response:
            return 0.0

        clarity_score = 1.0

        # Penalize for poor length
        words = len(response.split())
        if words < 10:
            clarity_score -= 0.3  # Too short
        elif words > 5000:
            clarity_score -= 0.1  # Too long

        # Check for structure (paragraphs, lists, etc.)
        has_structure = bool(
            '\n' in response or
            re.search(r'\d+\.|•|—|-', response)
        )
        if has_structure:
            clarity_score += 0.1

        # Check for jargon/readability
        complex_words = len(re.findall(r'\b[a-z]{15,}\b', response, re.IGNORECASE))
        if complex_words > len(response.split()) * 0.1:
            clarity_score -= 0.1

        return max(0.0, min(1.0, clarity_score))

    @trace_performance(operation='calculate_safety', component='llm_quality_monitor')
    @error_context(component='llm_quality_monitor', operation='calculate_safety')
    def _calculate_safety(self, response: str) -> float:
        """Evaluate response for safety/toxicity issues."""
        safety_score = 1.0

        response_lower = response.lower()        # Check for toxic content
        for category, keywords in self.SAFETY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in response_lower:
                    if category == 'toxic':
                        safety_score -= 0.3
                    elif category == 'harmful':
                        safety_score -= 0.4
                    else:
                        safety_score -= 0.2

        # Check for instructions to do harmful things
        if re.search(r'\b(?:how to|instructions for)\s+(?:hack|crack|exploit|abuse)\b',
                     response_lower):
            safety_score -= 0.5

        return max(0.0, min(1.0, safety_score))

    @trace_performance(operation='detect_hallucination_risk', component='llm_quality_monitor')
    @error_context(component='llm_quality_monitor', operation='detect_hallucination_risk')
    def _detect_hallucination_risk(self, response: str) -> float:
        """Detect likelihood of hallucination in response."""
        hallucination_risk = 0.0

        # Check for hallucination indicators
        for pattern in self.HALLUCINATION_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                hallucination_risk += 0.15

        # Check for overconfidence with uncertain language
        confidence_words = len(re.findall(
            r'\b(?:definitely|certainly|obviously|clearly|absolutely)\b',
            response,
            re.IGNORECASE
        ))
        uncertain_words = len(re.findall(
            r'\b(?:maybe|perhaps|possibly|might|could|seems)\b',
            response,
            re.IGNORECASE
        ))

        # High confidence with low uncertainty is suspicious
        if confidence_words > 3 and uncertain_words == 0:
            hallucination_risk += 0.2

        # Check for invented citations or references
        invented_refs = len(re.findall(
            r'\[(?:cite|ref|source):\s*(?:missing|unknown|not\s+found)\]',
            response,
            re.IGNORECASE
        ))
        hallucination_risk += invented_refs * 0.2

        return min(1.0, hallucination_risk)

    def _track_score(self, score: QualityScore) -> None:
        """Track quality score for analytics."""
        self.quality_history.append(score)

        stats = self.stats
        stats['responses_evaluated'] += 1

        # Update average quality
        count = stats['responses_evaluated']
        old_avg = stats['avg_quality_score']
        stats['avg_quality_score'] = (old_avg * (count - 1) + score.overall_score) / count

        # Track issues
        if score.hallucination_risk > 0.5:
            stats['hallucination_detections'] += 1
        if not score.is_safe:
            stats['safety_issues'] += 1

    def get_quality_trend(self, last_n: int = 10) -> List[float]:
        """Get recent quality scores."""
        return [s.overall_score for s in self.quality_history[-last_n:]]

    def get_average_quality(self) -> float:
        """Get average quality score."""
        if not self.quality_history:
            return 0.0
        return sum(s.overall_score for s in self.quality_history) / len(self.quality_history)

    def get_stats(self) -> Dict[str, Any]:
        """Get quality monitoring statistics."""
        return self.stats.copy()

    def get_quality_report(self, score: QualityScore) -> Dict[str, Any]:
        """Get detailed quality report."""
        return {
            'overall_score': round(score.overall_score, 3),
            'quality_level': score.quality_level.name,
            'scores': {
                'accuracy': round(score.accuracy_score, 3),
                'consistency': round(score.consistency_score, 3),
                'clarity': round(score.clarity_score, 3),
                'safety': round(score.safety_score, 3),
            },
            'hallucination_risk': round(score.hallucination_risk, 3),
            'is_safe': score.is_safe,
            'warnings': score.warnings,
            'timestamp': score.timestamp.isoformat(),
        }

    def reset_history(self) -> None:
        """Clear monitoring history."""
        self.quality_history = []
        self.stats = {
            'responses_evaluated': 0,
            'avg_quality_score': 0.0,
            'hallucination_detections': 0,
            'safety_issues': 0,
        }
        logger.info("Quality monitor history cleared")


# Global quality monitor instance
_quality_monitor: Optional[LLMQualityMonitor] = None


def get_quality_monitor() -> LLMQualityMonitor:
    """Get or create global quality monitor instance."""
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = LLMQualityMonitor()
    return _quality_monitor
