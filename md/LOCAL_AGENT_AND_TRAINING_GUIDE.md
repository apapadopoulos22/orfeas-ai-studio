# Local Agent Optimization and Minimal ML Training

This guide explains how to use the new local agent optimizer and the minimal ML training scaffold added to this workspace.

Contents

1. Local Agent Optimizer (backend/local_agent_optimizer.py)

2. Agent Demo (scripts/run_agent_demo.py)

3. Minimal ML Training (ml/train_loop.py)

4. Windows PowerShell Runner (ps1/RUN_MINIMAL_TRAINING.ps1)
5. Tips and Next Steps

## 1) Local Agent Optimizer

File: `backend/local_agent_optimizer.py`

Features:

- Register tools/abilities with metadata
- Concurrency control via semaphore
- Circuit breaker per ability with cooldown
- TTL result cache to avoid redundant work
- In-memory metrics; Prometheus export optional (if prometheus_client installed)

Quick use (Python):

```python
from backend.local_agent_optimizer import demo_agent
agent = demo_agent()
print(agent.call("uppercase", {"text": "orfeas"}))
print(agent.call("sum", {"a": 2, "b": 3}))
print(agent.metrics)

```text

Prometheus export:

```python
agent.start_metrics_exporter(port=9308)  # optional if prometheus_client is installed

```text

## 2) Agent Demo

File: `scripts/run_agent_demo.py`

Run:

```powershell
python .\scripts\run_agent_demo.py

```text

## 3) Minimal ML Training

File: `ml/train_loop.py`

What it does:

- Deterministic, config-driven linear regression on synthetic data (or CSV)
- Logs epoch loss and saves a JSON checkpoint to `ml/checkpoints/minimal.json`

Run (default config):

```powershell
python .\ml\train_loop.py

```text

Use from Python:

```python
from ml.train_loop import TrainConfig, train_linear_regression
cfg = TrainConfig(epochs=10, lr=0.05)
result = train_linear_regression(cfg)
print(result["w"], result["b"])  # learned parameters

```text

CSV input (two columns: `x,y` per line) can be passed via `TrainConfig(dataset_path=...)`.

## 4) Windows PowerShell Runner

File: `ps1/RUN_MINIMAL_TRAINING.ps1`

Run with custom params:

```powershell
powershell -ExecutionPolicy Bypass -File .\ps1\RUN_MINIMAL_TRAINING.ps1 -Epochs 8 -Lr 0.05 -BatchSize 32 -Seed 123 -Dataset "" -Checkpoint "./ml/checkpoints/minimal.json"

```text

Output: final loss and learned parameters, checkpoint saved under `ml/checkpoints/`.

## 5) Tips and Next Steps

- Replace the demo abilities with real tools (I/O, model inference, etc.).
- Tune circuit breaker threshold and cooldown to match reliability constraints.
- Extend `ml/train_loop.py` to PyTorch/TF as needed; wire real datasets and metrics.
- If you use Prometheus, point Grafana to the metrics port (default 9308).
