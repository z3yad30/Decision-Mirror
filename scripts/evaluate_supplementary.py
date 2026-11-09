from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.supplementary import RUN_IDS, evaluate_supplementary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write post-hoc supplementary analyses for saved runs."
    )
    parser.add_argument(
        "--run-id",
        action="append",
        dest="run_ids",
        help="Run ID to analyze; may be supplied more than once.",
    )
    args = parser.parse_args(argv)
    for run_id in args.run_ids or RUN_IDS:
        try:
            report = evaluate_supplementary(run_id)
        except (OSError, ValueError, KeyError) as error:
            print(f"Supplementary evaluation failed for {run_id}: {error}", file=sys.stderr)
            return 2
        print(
            f"Wrote supplementary outputs for {run_id} "
            f"({report['quiz_question_cluster_bootstrap']['cluster_count']} quiz clusters)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
