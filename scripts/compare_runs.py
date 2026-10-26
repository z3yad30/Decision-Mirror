from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.runner import evaluate_run


def _paired_report(
    run_a: str,
    run_b: str,
    items_a: list[dict[str, Any]],
    items_b: list[dict[str, Any]],
) -> dict[str, Any]:
    by_a = {row["item_id"]: row for row in items_a}
    by_b = {row["item_id"]: row for row in items_b}
    common = sorted(by_a.keys() & by_b.keys())
    paired: list[dict[str, Any]] = []
    comparison_rows: dict[str, list[tuple[float, float | None, float | None]]] = {}
    for item_id in common:
        row_a, row_b = by_a[item_id], by_b[item_id]
        if row_a["gold_set"] != row_b["gold_set"]:
            continue
        if row_a["gold_set"] == "quiz":
            trait_ids = [row_a["target_trait"]]
        elif row_a["gold_set"] == "organic":
            trait_ids = [f"T{index:02d}" for index in range(1, 6)]
        else:
            trait_ids = []
        for trait_id in trait_ids:
            gold_score = row_a.get(f"gold_score_{trait_id}")
            if gold_score is None or row_b.get(f"gold_score_{trait_id}") is None:
                continue
            score_a = row_a.get(f"score_{trait_id}")
            score_b = row_b.get(f"score_{trait_id}")
            comparison_rows.setdefault(trait_id, []).append(
                (float(gold_score), score_a, score_b)
            )
            delta = (
                score_b - score_a
                if score_a is not None and score_b is not None
                else None
            )
            paired.append(
                {
                    "item_id": item_id,
                    "trait_id": trait_id,
                    "gold_score": gold_score,
                    "score_a": score_a,
                    "score_b": score_b,
                    "delta_b_minus_a": delta,
                    "exact_band_a": _band(score_a) if score_a is not None else None,
                    "exact_band_b": _band(score_b) if score_b is not None else None,
                }
            )
    summary = {}
    for trait_id, rows in comparison_rows.items():
        numeric = [
            (gold, score_a, score_b)
            for gold, score_a, score_b in rows
            if score_a is not None and score_b is not None
        ]
        deltas = [score_b - score_a for _, score_a, score_b in numeric]
        summary[trait_id] = {
            "gold_non_null_n": len(rows),
            "non_null_rate_a": sum(score_a is not None for _, score_a, _ in rows)
            / len(rows),
            "non_null_rate_b": sum(score_b is not None for _, _, score_b in rows)
            / len(rows),
            "null_to_score_b_count": sum(
                score_a is None and score_b is not None
                for _, score_a, score_b in rows
            ),
            "score_to_null_b_count": sum(
                score_a is not None and score_b is None
                for _, score_a, score_b in rows
            ),
            "paired_numeric_n": len(numeric),
            "mae_a": (
                sum(abs(gold - score_a) for gold, score_a, _ in numeric)
                / len(numeric)
                if numeric else None
            ),
            "mae_b": (
                sum(abs(gold - score_b) for gold, _, score_b in numeric)
                / len(numeric)
                if numeric else None
            ),
            "exact_band_accuracy_a": (
                sum(_band(gold) == _band(score_a) for gold, score_a, _ in numeric)
                / len(numeric)
                if numeric else None
            ),
            "exact_band_accuracy_b": (
                sum(_band(gold) == _band(score_b) for gold, _, score_b in numeric)
                / len(numeric)
                if numeric else None
            ),
            "mean_score_delta_b_minus_a": (
                sum(deltas) / len(deltas) if deltas else None
            ),
            "mean_absolute_score_change": (
                sum(abs(value) for value in deltas) / len(deltas)
                if deltas else None
            ),
        }
    return {
        "run_a": run_a,
        "run_b": run_b,
        "common_item_count": len(common),
        "paired_gold_trait_count": len(paired),
        "paired_numeric_score_count": sum(
            row["score_a"] is not None and row["score_b"] is not None
            for row in paired
        ),
        "score_comparison_by_trait": summary,
        "paired_items": paired,
        "note": "Common gold-non-null traits are paired; null-to-score transitions are reported separately, and numeric score deltas use only non-null scores from both runs.",
    }


def _band(score: float) -> int:
    return min(int(float(score) * 5), 4)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare two saved extraction runs on common items."
    )
    parser.add_argument("run_a")
    parser.add_argument("run_b")
    args = parser.parse_args(argv)
    try:
        analysis_a = evaluate_run(args.run_a)
        analysis_b = evaluate_run(args.run_b)
        report = _paired_report(
            args.run_a,
            args.run_b,
            analysis_a["items"],
            analysis_b["items"],
        )
        output_dir = ROOT / "evaluation" / "comparisons"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{args.run_a}__vs__{args.run_b}.json"
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError, KeyError) as error:
        print(f"Comparison failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({
        "common_item_count": report["common_item_count"],
        "paired_numeric_score_count": report["paired_numeric_score_count"],
        "score_comparison_by_trait": report["score_comparison_by_trait"],
        "output": str(output_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
