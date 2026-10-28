# Decision Mirror

Decision Mirror is a research project for turning decision narratives and onboarding responses into structured, evidence-supported decision traits.

## Setup

From the repository root, create and activate a virtual environment, then install the pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set `GROQ_API_KEY` in `.env` before running any code that calls the Groq API. Do not commit `.env`.

## Repository layout

See [file_structure.txt](./file_structure.txt) for the generated repository tree.

## Available commands

Regenerate the tree:

```powershell
python scripts/update_file_structure.py
```

Run the test suite:

```powershell
pytest -q
```

## Running extraction

Activate `.venv`, configure `GROQ_API_KEY` in `.env`, and repeat each command
until it prints `RUN COMPLETE`. The runner handles at most 10 items per
invocation and resumes from saved progress:

```powershell
python scripts/run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split dev
```

`v2.0` is the frozen prompt selected for evaluation. `v2.1` remains a rejected
draft: its dev organic situational-factor recall was 66.7%, below the proposed
80.0% threshold. Do not use v2.1 as the final prompt. The stored v2.0 held-out
run is reproduced offline in the final Task 4 report.

To run a new held-out extraction (API call; do not use to reproduce the stored
evaluation):

```powershell
python scripts/run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split heldout --batch-size 10
```

The held-out split contains 56 items, so repeat the command until `RUN COMPLETE`
(six invocations: five batches of 10 and one batch of 6).

Check progress without an API call or preview the next batch with
`--status` or `--dry-run`:

```powershell
python scripts/run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split dev --status
python scripts/run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split dev --dry-run
```

Quota stops exit with code 3; rerun the same command later to resume. Full setup,
per-set invocation counts, retry behavior, and output locations are in
[`how_to_run.md`](./docs/tasks/task-4-llm-extraction/how_to_run.md).

## Evaluating a run

Evaluate saved responses offline (no API calls), then compare two runs on their
common items:

```powershell
python scripts/evaluate_run.py --run-id <run_id>
python scripts/compare_runs.py <run_a> <run_b>
```

Reports are written under `evaluation/results/<run_id>/` and paired comparisons
under `evaluation/comparisons/`. Evaluation methodology, metric formulas,
error taxonomy, and proposed readiness thresholds are documented in
[`04_evaluation_method.md`](./docs/tasks/task-4-llm-extraction/04_evaluation_method.md).

## Final Task 4 evaluation and reproduction

Task 4 implements frozen v1.0 extraction contracts, a versioned prompt, a
resumable API runner, offline validation and metrics, and the evaluation
handoff. **v2.0 is the frozen final prompt**; cite model
`openai/gpt-oss-120b` on Groq and prompt SHA-256
`6f93b33da4bf2193641bb47156b1ca090a84f86f718e69085513aae4e6d280d7`.
Quiz target exact-band accuracy was 67.1% dev / 65.2% held-out; MAE was
0.073 / 0.069. Organic situational-factor recall was 100% in each split, but
the held-out result comes from only six organic records and is not statistically
meaningful. Edge-case pass rate was 83.0% on dev only; there are no held-out
edge cases. The readiness decision is **Ready with conditions**, not
unconditional validation.

See the reproducible tables, limitations, criteria, examples, and approval line
in the [Task 4 evaluation report](./docs/tasks/task-4-llm-extraction/06_evaluation_report.md)
and the [profile-aggregation handoff](./docs/tasks/task-4-llm-extraction/07_handoff_to_profile_aggregation.md).
The report's reproduction section gives the exact fresh-clone commands; the
core offline evaluation commands are:

```powershell
python scripts/evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-dev__5825600d
python scripts/evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-heldout__5825600d
python scripts/build_task4_report.py
```

The manifest [`TASK4_MANIFEST.json`](./docs/tasks/task-4-llm-extraction/TASK4_MANIFEST.json)
freezes SHA-256 hashes for the contracts, prompt, datasets, raw final runs, and
metrics. No API key is needed for this reproduction.

## Data

- `data/gold/` contains the supplied 125-record quiz gold file (unchanged), the
  20-record organic transcription from Ontology §9, and self-authored
  behavior-only edge cases. Dataset provenance, limitations, and ambiguity
  notes are documented in
  [`gold_data.md`](./docs/tasks/task-4-llm-extraction/gold_data.md).
- `data/processed/` contains the fixed seed-42 split, the unified evaluation
  set, and its SHA-256 manifest. Rebuild the evaluation set and manifest with:

  ```powershell
  python scripts/build_eval_set.py
  ```

  The split must not be changed after an API run begins.

## Contracts

Task 4's frozen contracts are in [`schemas/`](./schemas/):
[`extraction_input.schema.json`](./schemas/extraction_input.schema.json),
[`extraction_output.schema.json`](./schemas/extraction_output.schema.json), and
[`extraction_result.schema.json`](./schemas/extraction_result.schema.json).
The field tables, semantic rules, and malformed-output policy are documented in
[`01_input_spec.md`](./docs/tasks/task-4-llm-extraction/01_input_spec.md) and
[`02_output_spec.md`](./docs/tasks/task-4-llm-extraction/02_output_spec.md).
Validate a JSON instance against a schema with:

```powershell
python -c "import json, jsonschema; jsonschema.validate(json.load(open(r'payload.json', encoding='utf-8')), json.load(open(r'schemas/extraction_input.schema.json', encoding='utf-8')))"
```

The example fixture sets are validated together with the schemas and semantic
rules by `pytest -q`.

## Prompts

Extraction prompt versions and their SHA-256 hashes are listed in
[`prompts/extraction/registry.json`](./prompts/extraction/registry.json).
`load_prompt(version)` returns the prompt text and its calculated hash; frozen
versions are hash-verified, and legacy versions require an explicit
`allow_legacy=True`. `v2.0` is frozen and selected; `v2.1` is an unselected
draft after its dev comparison failed the proposed situational-factor recall
threshold.

Never edit a frozen prompt in place. Create a new version, register its
parentage and hash, and explain the change in
[`CHANGELOG.md`](./prompts/extraction/CHANGELOG.md). Legacy prompts are
archived for provenance and are not used for official evaluation.

## Task 4 status

- [x] Prompt 1: environment, scaffold, source archive, and team review.
- [x] Prompt 2: frozen input/output contracts, validators, examples, and tests.
- [x] Prompt 3: gold datasets, edge cases, fixed split, and unified evaluation set.
- [x] Prompt 4: versioned extraction prompt, registry, leakage tests, and review checklist.
- [x] Prompt 5: resumable, rate-limit-safe extraction runner and run documentation.
- [x] Prompt 6: offline evaluation metrics, error taxonomy, paired comparison, and readiness criteria.
- [x] Prompt 7: dev-split error analysis, evidence-based v2.1 draft revision, and paired v2.0/v2.1 dev comparison.
- [x] Prompt 8: final evaluation report, conditional readiness decision, reproducibility freeze, and profile-aggregation handoff.

**Task 4 status:** Complete for a guarded downstream pilot, with conditions.
Team-lead approval and human evidence cross-review remain required; see the
report's blank approval line and readiness conditions.
