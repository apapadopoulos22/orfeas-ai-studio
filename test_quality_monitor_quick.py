#!/usr/bin/env python3
"""Quick test for llm_quality_monitor.py"""

from backend.llm_integration.llm_quality_monitor import LLMQualityMonitor

monitor = LLMQualityMonitor()

# Test good response
good_response = "Python is a high-level programming language created by Guido van Rossum. It emphasizes code readability and simplicity. Python uses indentation for code blocks."
score = monitor.evaluate_response(good_response, task_type="factual")

print(f'✓ Quality monitor works')
print(f'✓ Response quality: {score.overall_score:.2f} ({score.quality_level.name})')
print(f'✓ Safety: {score.safety_score:.2f}, Hallucination risk: {score.hallucination_risk:.2f}')
print(f'✓ Clarity: {score.clarity_score:.2f}, Consistency: {score.consistency_score:.2f}')
print(f'✓ Safe: {score.is_safe}, Warnings: {len(score.warnings)}')
print(f'✓ Monitor stats: {monitor.get_stats()}')
