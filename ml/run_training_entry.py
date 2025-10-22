from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from ml.train_loop import TrainConfig, train_linear_regression


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minimal training entrypoint")
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--lr", type=float, default=0.1)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--dataset", type=str, default="")
    p.add_argument("--checkpoint", type=str, default="./ml/checkpoints/minimal.json")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = TrainConfig(
        epochs=args.epochs,
        lr=args.lr,
        batch_size=args.batch_size,
        seed=args.seed,
        dataset_path=args.dataset if args.dataset else None,
        checkpoint_path=args.checkpoint,
    )
    result: Dict[str, Any] = train_linear_regression(cfg)
    final = {
        "w": result["w"],
        "b": result["b"],
        "loss": result["history"][-1]["loss"],
        "checkpoint": str(Path(cfg.checkpoint_path).resolve()),
    }
    print(json.dumps({"final": final}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
