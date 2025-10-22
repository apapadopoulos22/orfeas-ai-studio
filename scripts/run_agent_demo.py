from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from local_agent_optimizer import demo_agent  # noqa: E402


def main() -> int:
    agent = demo_agent()
    out1 = agent.call("uppercase", {"text": "orfeas"})
    out2 = agent.call("sum", {"a": 7, "b": 5})
    print(json.dumps({"uppercase": out1, "sum": out2, "metrics": agent.metrics}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
