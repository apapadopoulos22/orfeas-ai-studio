#!/usr/bin/env python3
"""Quick test for token_counter.py"""

from backend.llm_integration.token_counter import TokenCounter

tc = TokenCounter(10.0)
u = tc.count_tokens('gpt-4-turbo', 500, 200)
print('✓ Token counter works')
print(f'✓ Total cost: ${tc.get_total_cost():.6f}')
print(f'✓ Requests: {len(tc.usage_history)}')
stats = tc.get_summary_stats()
print(f'✓ Summary: {stats}')
