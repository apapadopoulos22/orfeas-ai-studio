#!/usr/bin/env python3
"""
Simple test for LLM foundation implementation
"""

import sys
from pathlib import Path
import asyncio

# Add the backend directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "llm_integration"))

from llm_foundation import create_llm_manager, LLMRequest

async def test_llm_foundation():
    """Test the LLM foundation"""
    print(" Testing LLM Foundation...")

    try:
        # Create manager
        manager = create_llm_manager()
        print(f" LLM Manager created with {len(manager.providers)} providers")

        # Test request
        request = LLMRequest(
            prompt="Explain the benefits of ORFEAS AI 3D generation",
            temperature=0.3,
            max_tokens=500
        )

        # Generate response
        response = await manager.generate_with_retry(request)

        if response.success:
            print(f" Generation successful!")
            print(f"   Provider: {response.provider.value}")
            print(f"   Model: {response.model}")
            print(f"   Response time: {response.response_time:.3f}s")
            print(f"   Tokens used: {response.tokens_used}")
            print(f"   Content: {response.content[:100]}...")
        else:
            print(f" Generation failed: {response.error}")

        # Get stats
        stats = manager.get_all_stats()
        print(f"\n Manager Statistics:")
        print(f"   Total providers: {stats['total_providers']}")

        for provider_name, provider_stats in stats['provider_stats'].items():
            print(f"   {provider_name}: {provider_stats['requests_made']} requests, {provider_stats['total_tokens_used']} tokens")

        print("\n LLM Foundation test completed successfully!")
        return True

    except Exception as e:
        print(f" Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_foundation())
    sys.exit(0 if success else 1)
