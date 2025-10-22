"""
Local LLM Performance Testing - Measure latency across varied prompt lengths
"""
import requests
import time
import statistics
from typing import List, Dict

def test_prompt_performance(prompt: str, description: str, iterations: int = 5) -> Dict:
    """Test a prompt multiple times and return performance metrics"""
    latencies = []

    for i in range(iterations):
        payload = {
            "prompt": prompt,
            "max_tokens": 100
        }

        start = time.time()
        try:
            response = requests.post(
                "http://localhost:5000/api/local-llm/generate",
                json=payload,
                timeout=10
            )
            elapsed_ms = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                latencies.append(elapsed_ms)
            else:
                print(f"  ⚠️ Request {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️ Request {i+1} error: {e}")

    if latencies:
        return {
            "description": description,
            "prompt_length": len(prompt),
            "iterations": len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
        }
    else:
        return {
            "description": description,
            "error": "All requests failed"
        }

def main():
    print("=" * 70)
    print("🚀 LOCAL LLM PERFORMANCE TESTING")
    print("=" * 70)
    print()

    # Check endpoint availability
    print("1️⃣ Checking endpoint availability...")
    try:
        response = requests.get("http://localhost:5000/api/local-llm/status", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Model: {config.get('model', 'unknown')}")
            print(f"   🌐 Server: {config.get('server', 'unknown')}")
            print()
        else:
            print(f"   ❌ Status endpoint returned: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot reach endpoint: {e}")
        return

    # Test scenarios with increasing prompt complexity
    test_cases = [
        {
            "prompt": "Hi",
            "description": "Minimal (2 chars)"
        },
        {
            "prompt": "What is 2+2?",
            "description": "Simple question (13 chars)"
        },
        {
            "prompt": "Explain the concept of machine learning in one sentence.",
            "description": "Medium complexity (59 chars)"
        },
        {
            "prompt": "Write a detailed explanation of how neural networks work, including the role of activation functions, backpropagation, and gradient descent. Keep it under 150 words.",
            "description": "Complex technical (178 chars)"
        },
        {
            "prompt": "Analyze the following scenario: A company wants to implement an AI system for customer service. What are the key considerations for data privacy, model accuracy, user experience, and scalability? Provide a structured response with at least 3 points for each consideration.",
            "description": "Long analytical prompt (311 chars)"
        }
    ]

    print("2️⃣ Running performance tests (5 iterations each)...")
    print()

    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {test_case['description']}")
        print(f"  Prompt length: {len(test_case['prompt'])} characters")

        result = test_prompt_performance(
            test_case['prompt'],
            test_case['description'],
            iterations=5
        )
        results.append(result)

        if 'error' not in result:
            print(f"  ⏱️  Mean latency: {result['mean_ms']:.1f}ms")
            print(f"  📊 Min/Max: {result['min_ms']:.1f}ms / {result['max_ms']:.1f}ms")
            print(f"  📈 Std Dev: {result['stdev_ms']:.1f}ms")
        else:
            print(f"  ❌ {result['error']}")
        print()

    # Summary analysis
    print("=" * 70)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 70)
    print()

    successful_results = [r for r in results if 'error' not in r]

    if successful_results:
        print(f"{'Test Description':<30} {'Prompt Len':<12} {'Mean (ms)':<12} {'Target':<12}")
        print("-" * 70)

        for result in successful_results:
            mean = result['mean_ms']
            target_met = "✅ PASS" if mean < 100 else "⚠️ SLOW" if mean < 200 else "❌ FAIL"
            print(f"{result['description']:<30} {result['prompt_length']:<12} {mean:<12.1f} {target_met}")

        print()
        print(f"Overall Performance:")
        all_means = [r['mean_ms'] for r in successful_results]
        print(f"  • Average across all tests: {statistics.mean(all_means):.1f}ms")
        print(f"  • Best performance: {min(all_means):.1f}ms")
        print(f"  • Worst performance: {max(all_means):.1f}ms")
        print()

        # Target assessment
        under_100ms = sum(1 for m in all_means if m < 100)
        print(f"✅ Tests under 100ms target: {under_100ms}/{len(successful_results)}")

        if under_100ms == len(successful_results):
            print("🎉 All tests met performance target!")
        elif under_100ms > len(successful_results) / 2:
            print("⚠️ Most tests met target, some optimization opportunities remain")
        else:
            print("❌ Performance below target for most tests")
    else:
        print("❌ No successful test results")

    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
