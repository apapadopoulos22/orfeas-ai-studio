"""
Minimal ML training scaffold (framework-agnostic)
-------------------------------------------------

This module provides a tiny, dependency-light training skeleton that can be
adapted to your data and models. It uses NumPy if available, but will fall
back to pure Python for demo purposes.

Features:
- Config-driven hyperparameters
- Deterministic seeding
- Simple synthetic dataset or user-provided CSV
- Training loop with metric logging
- Checkpoint save/load (JSON for simplicity)
"""
from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


try:  # optional
    import numpy as np  # type: ignore

    HAVE_NUMPY = True
except Exception:  # pragma: no cover
    np = None  # type: ignore
    HAVE_NUMPY = False


@dataclass
class TrainConfig:
    epochs: int = 5
    lr: float = 0.1
    batch_size: int = 16
    seed: int = 42
    dataset_path: str | None = None  # optional CSV with two columns: x,y
    checkpoint_path: str = "./ml/checkpoints/minimal.json"


def set_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as _np  # type: ignore

        _np.random.seed(seed)
    except Exception:
        pass


def load_dataset(cfg: TrainConfig) -> List[Tuple[float, float]]:
    if cfg.dataset_path and os.path.exists(cfg.dataset_path):
        rows: List[Tuple[float, float]] = []
        with open(cfg.dataset_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 2:
                    continue
                try:
                    x, y = float(parts[0]), float(parts[1])
                except ValueError:
                    continue
                rows.append((x, y))
        if rows:
            return rows
        logger.warning("Dataset file provided but no valid rows parsed; falling back to synthetic.")

    # synthetic y = 2x + 1 + noise
    rows = []
    for i in range(200):
        x = i / 10.0
        noise = (random.random() - 0.5) * 0.2
        y = 2.0 * x + 1.0 + noise
        rows.append((x, y))
    return rows


def shuffle_batches(data: List[Tuple[float, float]], batch_size: int) -> List[List[Tuple[float, float]]]:
    random.shuffle(data)
    return [data[i : i + batch_size] for i in range(0, len(data), batch_size)]


def mse(pred: float, target: float) -> float:
    d = pred - target
    return d * d


def train_linear_regression(cfg: TrainConfig) -> Dict[str, Any]:
    set_seed(cfg.seed)
    data = load_dataset(cfg)

    # Model params: y_hat = w * x + b
    w = 0.0
    b = 0.0

    history: List[Dict[str, float]] = []

    for epoch in range(1, cfg.epochs + 1):
        start = time.time()
        batches = shuffle_batches(data, cfg.batch_size)
        epoch_loss = 0.0
        n = 0

        for batch in batches:
            # Compute gradients over batch
            dw = 0.0
            db = 0.0
            for x, y in batch:
                y_hat = w * x + b
                err = y_hat - y
                dw += err * x
                db += err
                epoch_loss += mse(y_hat, y)
                n += 1

            # Average gradients and update
            bs = float(len(batch))
            if bs > 0:
                w -= cfg.lr * (dw / bs)
                b -= cfg.lr * (db / bs)

        epoch_time = (time.time() - start) * 1000.0
        avg_loss = epoch_loss / max(n, 1)
        logger.info(f"[ML] epoch={epoch} loss={avg_loss:.6f} w={w:.4f} b={b:.4f} time_ms={epoch_time:.2f}")
        history.append({"epoch": epoch, "loss": float(avg_loss), "w": float(w), "b": float(b), "time_ms": float(epoch_time)})

    result = {"w": float(w), "b": float(b), "config": cfg.__dict__, "history": history}
    save_checkpoint(cfg.checkpoint_path, result)
    return result


def save_checkpoint(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    logger.info(f"[ML] checkpoint saved: {path}")


def load_checkpoint(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    cfg = TrainConfig()
    out = train_linear_regression(cfg)
    print(json.dumps({"final": {"w": out["w"], "b": out["b"], "loss": out["history"][-1]["loss"]}}, indent=2))
