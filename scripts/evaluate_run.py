from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.runner import RESULTS_DIR, evaluate_run
from decision_mirror.extraction.prompt_loader import get_prompt_status


def _warn_if_unfrozen_heldout(run: dict[str, object]) -> None:
    if run.get("split") not in {"heldout", "all"}:
        return
    version = run.get("prompt_version")
    try:
        status = get_prompt_status(version) if isinstance(version, str) else "unregistered"
    except ValueError:
        status = "unregistered"
    if status != "frozen":
        print(
            "WARNING: HELD-OUT EVALUATION USED A NON-FROZEN PROMPT "
            f"(version={version!r}, registry_status={status!r}); "
            "treat these results as exploratory, not frozen held-out evidence.",
            file=sys.stderr,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate saved extraction responses without API calls."
    )
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    try:
        analysis = evaluate_run(args.run_id)
    except (OSError, ValueError, KeyError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 2
    _warn_if_unfrozen_heldout(analysis["metrics"]["run"])
    print(f"Evaluation written to {RESULTS_DIR / args.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
