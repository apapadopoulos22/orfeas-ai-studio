"""
Local Agent Optimizer
=====================

Lightweight, dependency-optional optimizer for local AI agents.

Features:
- Tool/ability registry with metadata
- Concurrency control (semaphore)
- Simple circuit breaker per tool
- Context-aware TTL cache for results
- Basic metrics (in-memory) with optional Prometheus export

Notes:
- No external deps required. If prometheus_client is installed, a metrics
  endpoint can be exposed via start_metrics_exporter().

"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple
import threading
import time
import json
import logging
import os

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


# Optional Prometheus support
try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server

    PROM_ENABLED = True
except Exception:  # pragma: no cover - optional
    Counter = Histogram = Gauge = None  # type: ignore
    start_http_server = None  # type: ignore
    PROM_ENABLED = False


@dataclass
class Ability:
    """Represents a single agent tool/ability."""

    name: str
    func: Callable[..., Any]
    description: str = ""
    tags: Tuple[str, ...] = ()
    version: str = "1.0"


@dataclass
class CircuitBreakerState:
    failures: int = 0
    last_failure_ts: float = 0.0
    open_until: float = 0.0


class TTLCache:
    """Simple thread-safe TTL cache keyed by (tool, params_json)."""

    def __init__(self, default_ttl: float = 30.0, max_items: int = 512) -> None:
        self.default_ttl = default_ttl
        self.max_items = max_items
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def _prune(self) -> None:
        now = time.time()
        keys_to_delete = [k for k, (exp, _) in self._cache.items() if exp < now]
        for k in keys_to_delete:
            del self._cache[k]
        # Simple size control
        if len(self._cache) > self.max_items:
            # Drop oldest by expiry
            for k, _ in sorted(self._cache.items(), key=lambda kv: kv[1][0])[: len(self._cache) - self.max_items]:
                self._cache.pop(k, None)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._prune()
            entry = self._cache.get(key)
            if not entry:
                return None
            exp, value = entry
            if exp < time.time():
                self._cache.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            self._prune()
            expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
            self._cache[key] = (expiry, value)


class LocalAgent:
    """Local agent with optimization primitives.

    - Register abilities (tools) with metadata
    - Execute with concurrency controls and circuit breaker per tool
    - Cache results with configurable TTL
    - Collect basic metrics and optionally export Prometheus metrics
    """

    def __init__(
        self,
        max_concurrency: int = 4,
        cache_ttl_seconds: float = 30.0,
        breaker_failure_threshold: int = 5,
        breaker_cooldown_seconds: float = 30.0,
    ) -> None:
        self._abilities: Dict[str, Ability] = {}
        self._lock = threading.Semaphore(max_concurrency)
        self._breaker_cfg = (breaker_failure_threshold, breaker_cooldown_seconds)
        self._breaker_state: Dict[str, CircuitBreakerState] = {}
        self._cache = TTLCache(cache_ttl_seconds)

        # Metrics
        self.metrics = {
            "calls_total": 0,
            "success_total": 0,
            "failure_total": 0,
            "breaker_open_total": 0,
            "latency_sum_ms": 0.0,
        }

        if PROM_ENABLED:
            self._m_calls = Counter("agent_calls_total", "Total agent ability calls", ["ability"])  # type: ignore
            self._m_success = Counter("agent_success_total", "Successful ability calls", ["ability"])  # type: ignore
            self._m_failure = Counter("agent_failure_total", "Failed ability calls", ["ability"])  # type: ignore
            self._m_breaker = Counter("agent_breaker_open_total", "Circuit breaker opens", ["ability"])  # type: ignore
            self._m_latency = Histogram("agent_latency_ms", "Ability latency (ms)", ["ability"])  # type: ignore

    # -------- Ability Registry --------
    def register(self, name: str, func: Callable[..., Any], description: str = "", tags: Tuple[str, ...] = (), version: str = "1.0") -> None:
        if name in self._abilities:
            raise ValueError(f"Ability already registered: {name}")
        self._abilities[name] = Ability(name=name, func=func, description=description, tags=tags, version=version)
        self._breaker_state[name] = CircuitBreakerState()
        logger.info(f"[Agent] Registered ability '{name}' (v{version})")

    def abilities(self) -> Dict[str, Dict[str, Any]]:
        return {
            k: {
                "description": v.description,
                "tags": list(v.tags),
                "version": v.version,
            }
            for k, v in self._abilities.items()
        }

    # -------- Execution --------
    def _cache_key(self, ability: str, params: Dict[str, Any]) -> str:
        try:
            params_json = json.dumps(params, sort_keys=True, default=str)
        except Exception:
            params_json = str(params)
        return f"{ability}:{params_json}"

    def _is_breaker_open(self, ability: str) -> bool:
        state = self._breaker_state.get(ability)
        if not state:
            return False
        if state.open_until > time.time():
            return True
        return False

    def _record_failure(self, ability: str) -> None:
        threshold, cooldown = self._breaker_cfg
        st = self._breaker_state[ability]
        st.failures += 1
        st.last_failure_ts = time.time()
        if st.failures >= threshold:
            st.open_until = time.time() + cooldown
            self.metrics["breaker_open_total"] += 1
            if PROM_ENABLED:
                self._m_breaker.labels(ability).inc()  # type: ignore
            logger.warning(f"[Agent] Circuit breaker OPEN for '{ability}' ({threshold} failures)")

    def _record_success(self, ability: str) -> None:
        st = self._breaker_state[ability]
        st.failures = 0
        st.open_until = 0.0

    def call(self, ability: str, params: Optional[Dict[str, Any]] = None, use_cache: bool = True, cache_ttl: Optional[float] = None) -> Any:
        """Execute an ability with optimization protections.

        Args:
            ability: Registered ability name
            params: Dict of parameters passed to underlying function
            use_cache: If True, attempts cache lookup and stores result
            cache_ttl: Optional TTL override for this call

        Raises:
            KeyError: If ability not registered
            RuntimeError: If circuit breaker is open
        """
        if ability not in self._abilities:
            raise KeyError(f"Unknown ability: {ability}")

        if self._is_breaker_open(ability):
            self.metrics["failure_total"] += 1
            if PROM_ENABLED:
                self._m_failure.labels(ability).inc()  # type: ignore
            raise RuntimeError(f"Circuit breaker open for '{ability}'")

        params = params or {}
        cache_key = self._cache_key(ability, params)

        if use_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.debug(f"[Agent] Cache hit for {ability}")
                return cached

        start = time.time()
        self.metrics["calls_total"] += 1
        if PROM_ENABLED:
            self._m_calls.labels(ability).inc()  # type: ignore

        with self._lock:
            try:
                result = self._abilities[ability].func(**params)
                self._record_success(ability)
                self.metrics["success_total"] += 1
                latency_ms = (time.time() - start) * 1000.0
                self.metrics["latency_sum_ms"] += latency_ms
                if PROM_ENABLED:
                    self._m_success.labels(ability).inc()  # type: ignore
                    self._m_latency.labels(ability).observe(latency_ms)  # type: ignore

                if use_cache:
                    self._cache.set(cache_key, result, ttl=cache_ttl)
                return result
            except Exception as e:  # noqa: BLE001 - broad by design to trip breaker
                self._record_failure(ability)
                self.metrics["failure_total"] += 1
                if PROM_ENABLED:
                    self._m_failure.labels(ability).inc()  # type: ignore
                logger.error(f"[Agent] Ability '{ability}' failed: {e}")
                raise

    # -------- Metrics Export --------
    def start_metrics_exporter(self, port: int = 9308) -> bool:
        """Start Prometheus metrics exporter if available.

        Returns True if exporter started, False otherwise.
        """
        if not PROM_ENABLED or start_http_server is None:
            logger.info("[Agent] Prometheus not installed; skipping exporter")
            return False
        try:
            start_http_server(port)
            logger.info(f"[Agent] Prometheus exporter running on :{port}")
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(f"[Agent] Prometheus exporter failed: {e}")
            return False


def _demo_uppercase(text: str) -> Dict[str, Any]:
    """Simple demo ability: returns text and uppercase form."""
    time.sleep(0.05)
    return {"input": text, "upper": text.upper()}


def _demo_sum(a: int, b: int) -> Dict[str, Any]:
    time.sleep(0.02)
    return {"a": a, "b": b, "sum": a + b}


def demo_agent() -> LocalAgent:
    """Create a demo-configured agent for quick manual tests."""
    agent = LocalAgent(max_concurrency=4)
    agent.register("uppercase", _demo_uppercase, description="Uppercase a string", tags=("text",))
    agent.register("sum", _demo_sum, description="Sum integers", tags=("math",))
    return agent


if __name__ == "__main__":  # Manual quick test
    ag = demo_agent()
    print("Abilities:", json.dumps(ag.abilities(), indent=2))
    print(ag.call("uppercase", {"text": "orfeas"}))
    print(ag.call("sum", {"a": 2, "b": 3}))
    print("Metrics:", json.dumps(ag.metrics, indent=2))
