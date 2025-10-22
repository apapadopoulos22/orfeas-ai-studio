#!/usr/bin/env python3
"""Quick test for llm_failover_handler.py"""

from backend.llm_integration.llm_failover_handler import LLMFailoverHandler, ErrorCategory

handler = LLMFailoverHandler(
    fallback_chain=["gpt-3.5-turbo", "claude-3-sonnet", "mistral-large"],
    circuit_failure_threshold=5,
    circuit_recovery_timeout_sec=60,
)

# Test circuit status
print('✓ Failover handler works')
print(f'✓ Circuit status: {list(handler.get_circuit_status().keys())[:3]} models')

# Test error categorization
error_429 = handler._categorize_error("Rate limit exceeded: 429")
error_timeout = handler._categorize_error("Request timeout")
print(f'✓ Error categorization: 429={error_429.value}, timeout={error_timeout.value}')

# Test backoff calculation
backoff = handler._calculate_backoff(2)
print(f'✓ Backoff calculated: {backoff:.2f}s')

# Test failover chain
fallover = handler._get_failover_model("gpt-4-turbo")
print(f'✓ Failover chain: primary=gpt-4-turbo -> fallback={fallover}')

print(f'✓ Handler stats: {handler.get_stats()}')
