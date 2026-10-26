from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.runner import RESULTS_DIR, evaluate_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate saved extraction responses without API calls."
    )
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    try:
        evaluate_run(args.run_id)
    except (OSError, ValueError, KeyError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 2
    print(f"Evaluation written to {RESULTS_DIR / args.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
