"""
Phase 3.1 Performance Benchmarking Suite
Measures latency and throughput for all components
"""

import sys
import os
import time
import statistics
from typing import Dict, List, Callable, Any
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Benchmark suite for Phase 3.1 components."""

    def __init__(self, iterations: int = 10):
        self.iterations = iterations
        self.results: Dict[str, Dict[str, Any]] = {}

    def benchmark_function(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
    ) -> Dict[str, float]:
        """Benchmark a single function."""
        if kwargs is None:
            kwargs = {}

        latencies = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
                end = time.perf_counter()
                latencies.append((end - start) * 1000)  # Convert to ms
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
                return {}

        result = {
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "avg_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "iterations": self.iterations,
        }

        self.results[name] = result
        logger.info(f"{name}: avg={result['avg_ms']:.2f}ms, median={result['median_ms']:.2f}ms")
        return result

    def print_report(self):
        """Print benchmark report."""
        print("\n" + "=" * 80)
        print("PHASE 3.1 PERFORMANCE BENCHMARK REPORT")
        print("=" * 80)

        target_ms = 1000.0
        total_tests = 0
        passed_tests = 0

        if not self.results:
            print("No results to report")
            return 0, 0

        for name, metrics in self.results.items():
            avg = metrics["avg_ms"]
            median = metrics["median_ms"]
            target_status = "✅ PASS" if avg < target_ms else "❌ FAIL"

            print(f"\n{name}")
            print(f"  Average: {avg:.2f}ms (median: {median:.2f}ms)")
            print(f"  Range: {metrics['min_ms']:.2f}ms - {metrics['max_ms']:.2f}ms")
            print(f"  Status: {target_status} (target: <{target_ms}ms)")

            total_tests += 1
            if avg < target_ms:
                passed_tests += 1

        print("\n" + "=" * 80)
        if total_tests > 0:
            print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
            print(f"Pass Rate: {100 * passed_tests / total_tests:.1f}%")
        print("=" * 80 + "\n")

        return passed_tests, total_tests


def run_phase_3_1_benchmarks():
    """Run all Phase 3.1 component benchmarks."""
    benchmark = PerformanceBenchmark(iterations=10)

    # Test 1: LLM Router
    def test_llm_router():
        from backend.llm_integration.llm_router import LLMRouter
        router = LLMRouter()
        router.select_model(
            task="code_generation",
            context_length=500,
            cost_sensitivity="medium"
        )

    benchmark.benchmark_function("LLM Router Selection", test_llm_router)

    # Test 2: Multi-LLM Orchestrator
    def test_orchestrator():
        from backend.llm_integration.multi_llm_orchestrator import MultiLLMOrchestrator
        orchestrator = MultiLLMOrchestrator()
        models = ["gpt-4", "claude-3-sonnet"]
        orchestrator.execute_parallel("test prompt", models=models, max_workers=2)

    benchmark.benchmark_function("Multi-LLM Orchestrator Parallel", test_orchestrator)

    # Test 3: Prompt Engineering
    def test_prompt_engineering():
        from backend.llm_integration.prompt_engineering import (
            PromptEngineer,
            PromptContext,
        )
        engineer = PromptEngineer()
        engineer.optimize_prompt(
            "What is AI?",
            context=PromptContext(
                task_type="explanation",
                complexity_level="simple",
                domain="AI",
            ),
        )

    benchmark.benchmark_function("Prompt Engineering Optimization", test_prompt_engineering)

    # Test 4: LLM Cache Layer - Set Operation
    def test_cache_set():
        from backend.llm_integration.llm_cache_layer import LLMCacheLayer
        cache = LLMCacheLayer(max_size=100, default_ttl_seconds=3600)
        cache.set("test_prompt", "test_response", model="gpt-4")

    benchmark.benchmark_function("Cache Layer Set Operation", test_cache_set)

    # Test 5: LLM Cache Layer - Get Hit
    def test_cache_get_hit():
        from backend.llm_integration.llm_cache_layer import LLMCacheLayer
        cache = LLMCacheLayer(max_size=100, default_ttl_seconds=3600)
        cache.set("test_prompt", "test_response", model="gpt-4")
        cache.get("test_prompt", model="gpt-4")

    benchmark.benchmark_function("Cache Layer Get Hit", test_cache_get_hit)

    # Test 6: Semantic Chunking
    def test_semantic_chunking():
        from backend.llm_integration.semantic_chunking import SemanticChunker
        chunker = SemanticChunker(strategy="semantic", chunk_size=100)
        text = "This is a sample text. " * 50
        chunker.chunk_document(text)

    benchmark.benchmark_function("Semantic Chunking", test_semantic_chunking)

    # Test 7: Context Retrieval
    def test_context_retrieval():
        from backend.llm_integration.context_retrieval import ContextRetriever
        docs = [
            {"content": f"Document {i}", "metadata": {"id": i}}
            for i in range(10)
        ]
        retriever = ContextRetriever(docs, strategy="hybrid", top_k=3)
        retriever.retrieve_context("test query")

    benchmark.benchmark_function("Context Retrieval Hybrid", test_context_retrieval)

    # Test 8: Token Counter
    def test_token_counter():
        from backend.llm_integration.token_counter import TokenCounter
        counter = TokenCounter(budget_limit_usd=10.0)
        counter.count_tokens("gpt-4-turbo", input_tokens=100, output_tokens=50)

    benchmark.benchmark_function("Token Counter", test_token_counter)

    # Test 9: Quality Monitor
    def test_quality_monitor():
        from backend.llm_integration.llm_quality_monitor import LLMQualityMonitor
        monitor = LLMQualityMonitor()
        monitor.evaluate_response("This is a test response from the LLM.")

    benchmark.benchmark_function("Quality Monitor Evaluation", test_quality_monitor)

    # Test 10: Failover Handler
    def test_failover_handler():
        from backend.llm_integration.llm_failover_handler import LLMFailoverHandler
        handler = LLMFailoverHandler(
            fallback_chain=["gpt-4", "gpt-3.5-turbo"],
            circuit_failure_threshold=3
        )
        handler.get_stats()

    benchmark.benchmark_function("Failover Handler Stats", test_failover_handler)

    # Print final report
    passed, total = benchmark.print_report()

    return benchmark.results, passed, total


if __name__ == "__main__":
    results, passed, total = run_phase_3_1_benchmarks()
