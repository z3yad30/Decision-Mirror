# Decision Mirror Project Guide

## Table of contents

1. [What this repository is](#1-what-this-repository-is)
2. [Quick start on Windows PowerShell](#2-quick-start-on-windows-powershell)
3. [Glossary](#3-glossary)
4. [Big-picture data flow](#4-big-picture-data-flow)
5. [Script-by-script execution walkthrough](#5-script-by-script-execution-walkthrough)
6. [File-by-file inventory](#6-file-by-file-inventory)
7. [The data in detail](#7-the-data-in-detail)
8. [Contracts](#8-contracts)
9. [Prompts](#9-prompts)
10. [Evaluation explained](#10-evaluation-explained)
11. [Results snapshot](#11-results-snapshot)
12. [Invariants and do not do this](#12-invariants-and-do-not-do-this)
13. [How-to recipes](#13-how-to-recipes)
14. [FAQ and troubleshooting](#14-faq-and-troubleshooting)
15. [Open items and limitations](#15-open-items-and-limitations)

## 1. What this repository is

Decision Mirror in five lines:

1. A research project about describing how people make decisions.
2. Its Task 4 stage extracts six defined traits from short onboarding answers and decision narratives.
3. The extractor returns structured scores, evidence quotations, confidence, and situational factors.
4. Versioned prompts, frozen JSON contracts, curated gold data, and offline metrics make the experiment traceable.
5. The current handoff is a guarded research pilot, not a validated or production decision system.

**Task 4 covers:** input/output contracts v1.0; quiz, organic, and qualitative edge-case evaluation data; a versioned extraction prompt; a resumable Groq API runner; strict offline validation and metrics; and a profile-aggregation handoff.

**Task 4 does not cover:** profile aggregation itself, durable user storage, retrieval, advisory/recommendation logic, a user interface, longitudinal T06 scoring, clinical validation, or production fitness. These are not implemented in the current repository.

`src/decision_mirror/extraction/` is the implemented application area. The `quiz`, `profiling`, `retrieval`, `advisory`, `storage`, and `common` packages under `src/decision_mirror/` are placeholders: each currently contains only `__init__.py`, with no feature implementation.

## 2. Quick start on Windows PowerShell

From the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
```

Activation can fail on a machine whose PowerShell execution policy blocks scripts. Do not change the machine policy just to run this project; use the venv interpreter directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest -q
```

Evaluate the committed v2.0 development run offline (no API key or API call):

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-dev__5825600d
```

Run a new extraction only when you intend to use the API and spend quota. Copy the example environment file, add your own `GROQ_API_KEY` to the local `.env`, then invoke the runner. Do not share or commit `.env`; its contents are intentionally not documented here. The example variable names and defaults are in [`.env.example`](../.env.example).

```powershell
Copy-Item .env.example .env
# Add GROQ_API_KEY to .env using your editor; never print its contents.
.\.venv\Scripts\python.exe scripts\run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split dev --batch-size 10
```

## 3. Glossary

| Term | Meaning |
|---|---|
| Gold | Human- or author-supplied reference labels and expected behavior used to evaluate a model; gold is not sent to the model. |
| Payload | The validated input object prepared for extraction; the evaluator stores it separately from each item's gold labels. |
| Eval set | The unified collection of payloads, gold, set names, and split assignments in `data/processed/eval_set_v1.json`. |
| Split | The fixed assignment of items to `dev` (development/prompt iteration) or `heldout` (reserved evaluation); edge cases are dev-only. |
| Prompt version | A named revision of the system instruction, such as `v2.0` or `v2.1`. |
| Registry | `prompts/extraction/registry.json`, mapping prompt versions to files, SHA-256 values, status, parent, date, and summary. |
| Frozen | A version intended not to change in place; the loader verifies a frozen prompt's file hash against the registry. |
| Raw response | The verbatim model response plus per-call metadata saved to `evaluation/runs/v2.0__openai-gpt-oss-120b__all-dev__5825600d/raw_responses.jsonl`; it is not the scored results table. |
| Run | One extraction configuration over a selected set and split, with its run manifest, raw responses, and attempt log. |
| Run ID | `<prompt>__<model-slug>__<set>-<split>__<first-8-eval-set-SHA-256>`; `--new-run` adds a UTC timestamp suffix to the directory name. |
| Manifest | A JSON record of the inputs/configuration and hashes that identify a dataset or run. |
| SHA-256 fingerprint | A 64-hex-character digest of file bytes used to detect changes; the eval-set hash prefix also contributes to run identity. |
| Band | One of five score intervals: `[0,.2)`, `[.2,.4)`, `[.4,.6)`, `[.6,.8)`, and `[.8,1]`. |
| MAE | Mean absolute error: the average of `abs(gold score - predicted score)` over paired numeric scores. |
| Confidence | The model's evidence-quality indicator, not a calibrated probability or confidence that a person's choice is correct. |
| Situational factor | A decision-specific circumstance/constraint represented separately from a stable trait. |
| Ambiguous gold | An organic annotation explicitly flagged as ambiguous; it is excluded from headline organic metrics and shown separately. |

## 4. Big-picture data flow

```text
data/gold/quiz_gold_v1.0.json
data/gold/organic_gold_v1.0.json
data/gold/edge_cases_v1.0.json
data/processed/split_v1.json
          |
          v
scripts/build_eval_set.py  [NO API]
          |
          v
data/processed/eval_set_v1.json + data/processed/MANIFEST.json
          |
          +------------------------+
          |                        |
          v                        v
prompts/extraction/registry.json   .env settings/key
prompts/extraction/extraction_v2.0.md
          \                        /
           \                      /
            v                    v
           scripts/run_extraction.py  [API CALL]
                      |
                      v
evaluation/runs/v2.0__openai-gpt-oss-120b__all-dev__5825600d/raw_responses.jsonl
                      |
                      v
       scripts/evaluate_run.py  [NO API]
                      |
                      v
evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/
                      |
                      v
       scripts/build_task4_report.py  [NO API]
                      |
                      v
docs/tasks/task-4-llm-extraction/06_evaluation_report.md
```

The only API-calling step in this flow is `run_extraction.py`. `compare_runs.py` also evaluates saved responses and writes a paired comparison, without an API call. The report builder reads stored run metrics and writes the report plus `TASK4_MANIFEST.json`.

## 5. Script-by-script execution walkthrough

All commands below use the repository root as the working directory. Only `run_extraction.py`, `evaluate_run.py`, and `compare_runs.py` define command-line parsers. The other three scripts have no `--help` implementation: passing `--help` to them runs their normal operation.

### `scripts/build_eval_set.py`

- **Purpose and CLI:** rebuild the unified evaluation set and its manifest. No flags or arguments.
- **When run:** (1) reads the three gold files and frozen split; (2) maps quiz records through `build_quiz_payload()` in `src/decision_mirror/extraction/payloads.py`, while organic/edge payloads are assembled locally; (3) assigns split and gold fields in `build_eval_set()`; (4) writes `data/processed/eval_set_v1.json`, computes SHA-256 for the gold files, split, and eval set, then writes `data/processed/MANIFEST.json`.
- **Inputs:** `data/gold/quiz_gold_v1.0.json`, `data/gold/organic_gold_v1.0.json`, `data/gold/edge_cases_v1.0.json`, `data/processed/split_v1.json`.
- **Outputs:** `data/processed/eval_set_v1.json` and `data/processed/MANIFEST.json`.
- **Validation, refusal, and exit:** the script does not invoke JSON Schema validation; the eval-set tests check the generated payloads and determinism. A missing/malformed source fails with an uncaught Python error (non-zero process exit); success exits 0. No API, retry, or resume logic.

### `scripts/run_extraction.py`

- **Purpose:** send one batch of evaluation items to Groq and resume a persistent run.
- **Flags and defaults:** `--prompt` (required; no default); `--set {quiz,organic,edge,all}` (required); `--split {dev,heldout,all}` (required); `--batch-size` (10, permitted 1–10); `--model` (unset means `GROQ_MODEL`, then `openai/gpt-oss-20b`); `--status` (false); `--dry-run` (false); `--retry-api-failures` (false); `--new-run` (false). `-h/--help` is provided by `argparse`.
- **Environment defaults:** `GROQ_TEMPERATURE=0`, `GROQ_MAX_TOKENS=4096`, `GROQ_REASONING_EFFORT=medium`, `REQUEST_DELAY_SECONDS=3`; see [`.env.example`](../.env.example). `GROQ_API_KEY` is required when the client is constructed.
- **When you run it:** (1) parses flags; `--status` reports existing run folders and exits before API setup; (2) loads the prompt with `load_prompt()` from `src/decision_mirror/extraction/prompt_loader.py`; (3) reads the eval set, hashes its bytes, filters by set/split, and derives the run ID; (4) builds/compares the manifest and reads saved response/attempt JSONL; (5) selects the first pending items up to batch size (or prints them for `--dry-run`); (6) creates a `GroqClient` unless a test client was injected; (7) for each selected item calls `run_item()` in `src/decision_mirror/extraction/pipeline.py`, which builds the model whitelist via `build_model_request()` in `payloads.py`, computes a request hash, and calls the client; (8) appends each successful model completion verbatim to `raw_responses.jsonl`, or logs API failures in `attempts.log.jsonl`; (9) classifies completed response text with `classify_response()` in `src/decision_mirror/extraction/validation.py` for the printed strict-valid count.
- **Inputs:** eval set, registered prompt, environment, and—on resume—existing run manifest and JSONL files.
- **Outputs:** a folder under `evaluation/runs/` containing `manifest.json`, `raw_responses.jsonl`, and `attempts.log.jsonl`; these are the files present in each of the three checked-in run folders. Each response record includes the item ID, verbatim response, reasoning when separately returned, finish reason, usage, latency, timestamp, request hash, model/prompt data, and attempt count.
- **Resume and mismatches:** already completed item IDs are skipped; duplicate final IDs and invalid JSONL fail. Partial final JSONL tails are repaired on normal resume. An existing run without a manifest is refused. A manifest mismatch in prompt/version hash, model/settings, response format, eval-set hash, split, or batch size is refused with guidance to change nothing or use `--new-run`; new runs preserve old folders.
- **Rate limits and malformed responses:** typed 429s are attempted up to three times, honoring `Retry-After` when supplied and sleeping between attempts; after the third, completed work is retained, the item remains pending, and the script returns **3**. Other transient API failures get in-invocation retries only with `--retry-api-failures` (up to three attempts). Completed malformed model text is still saved as a final response and is not called again; evaluation reports it as invalid.
- **What it refuses / does not enforce:** refuses legacy or unknown prompts, frozen prompts whose registered hash differs, invalid batch sizes, missing/invalid existing run state, and mismatched resume configuration. It does **not** enforce that a held-out run uses a frozen (rather than draft) prompt; the operator must enforce this invariant. Normal success/incomplete batch returns 0; quota exhaustion returns 3; caught `ValueError`/`RuntimeError` returns 2.

### `scripts/evaluate_run.py`

- **Purpose and CLI:** evaluate one saved run offline. `--run-id` is required; no default; `-h/--help` is supported.
- **When you run it:** (1) parses the run ID; (2) `evaluate_run()` in `evaluation/runner.py` reads the run manifest and raw JSONL; (3) verifies the manifest eval-set SHA-256 against the current eval-set file and joins saved responses to selected items; (4) attaches organic gold evidence from `data/gold/organic_gold_v1.0.json`; (5) calls `analyze_items()` in `evaluation/metrics.py`, which uses the strict contract validator; (6) writes metrics, per-item CSV, error log, schema-compliance JSON, tables, and difficult cases.
- **Inputs:** run manifest/raw responses, `data/processed/eval_set_v1.json`, organic gold.
- **Outputs:** six files under `evaluation/results/`: `metrics.json`, `per_item.csv`, `error_log.jsonl`, `schema_compliance.json`, `tables.md`, and `difficult_cases.md`.
- **Refusal and exit:** a missing run/input, invalid JSONL, duplicate/unknown response IDs, or eval-set hash mismatch fails; the hash error explicitly requires the original matching eval set. No API calls, resume, or response repair. Success returns 0; caught `OSError`, `ValueError`, or `KeyError` returns 2.

### `scripts/compare_runs.py`

- **Purpose and CLI:** compare two saved run IDs on common gold items. Positional arguments `run_a` and `run_b` are both required; no defaults; `-h/--help` is supported.
- **When you run it:** (1) parses the two IDs; (2) calls `evaluate_run()` for each, thereby refreshing both runs' offline result directories; (3) `_paired_report()` in the script joins common IDs, filters by matching gold set, compares quiz target traits and organic T01–T05, and counts null transitions separately from paired numeric deltas; (4) writes JSON to `evaluation/comparisons/`.
- **Inputs/outputs:** the two runs and evaluator inputs; one paired comparison JSON. No API calls.
- **Refusal and exit:** propagates missing/hash-invalid/duplicate run failures to its handler; success returns 0, caught `OSError`, `ValueError`, or `KeyError` returns 2.

### `scripts/build_task4_report.py`

- **Purpose and CLI:** rebuild the Task 4 report and its freeze manifest. No flags or arguments.
- **When you run it:** (1) `validate_frozen_status()` checks that the registry records v2.0 as frozen with the expected hash and that both v1.0 contract docs say they are frozen; (2) `load_run()` reads and checks v2.0 dev, v2.0 held-out, and v2.1 dev metrics/manifests; (3) verifies the candidate is v2.1 and raw response counts match metrics; (4) `create_report()` reads gold/split/eval data and saved raw responses and renders report tables/cases; (5) overwrites `docs/tasks/task-4-llm-extraction/06_evaluation_report.md` and writes `docs/tasks/task-4-llm-extraction/TASK4_MANIFEST.json`.
- **Inputs/outputs:** frozen registry/contracts, three metrics/manifests/runs, gold/split/eval data, and prompt text; report and Task 4 artifact manifest. No API calls.
- **Refusal and exit:** aborts on a frozen-status/hash, run ID/prompt hash, candidate version, or response-count mismatch and on missing/malformed inputs. No CLI parser means `--help` does not display help: it runs the builder. Success exits 0; uncaught errors exit non-zero. The report's generated date changes on each run.

### `scripts/update_file_structure.py`

- **Purpose and CLI:** regenerate root `file_structure.txt`; no flags or arguments.
- **When you run it:** (1) starts at repository root; (2) `render_tree()` recursively lists entries, omitting `.venv`, `.git`, `__pycache__`, `.pytest_cache`, and `*.egg-info`; (3) adds descriptions to selected root folders; (4) overwrites `file_structure.txt`.
- **Inputs/outputs and exit:** current filesystem tree in, generated tree file out; no API. It has no argument parser, so `--help` runs the tree writer. Success exits 0; uncaught filesystem errors exit non-zero.

## 6. File-by-file inventory

The “editable?” column describes intended stewardship, not filesystem permissions. Generated outputs should be regenerated rather than hand-edited; frozen inputs should not be changed in place.

### `data/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `data/gold/quiz_gold_v1.0.json` | Supplied onboarding quiz gold | 25 questions and 125 answer records; each answer has one target trait/value, evidence, confidence, and situation fields | Task 3 source | Eval-set builder and evaluator | Frozen source gold |
| `data/gold/organic_gold_v1.0.json` | Organic narrative gold | 20 records with decision text, T01–T06 annotations, gold evidence/factor, ambiguity flags/notes | Transcribed from ontology §9 | Builder and evaluator | Frozen transcription |
| `data/gold/edge_cases_v1.0.json` | Qualitative edge checks | 11 self-authored narratives with expected behavior assertions, not numeric score labels | Hand-written test data | Builder and evaluator | Frozen for this set/version |
| `data/gold/CHECKSUMS.txt` | Gold checksum list | SHA-256 entry for the quiz gold file | Hand-maintained | Human integrity checks | Hand-written; update only by approved data versioning |
| `data/processed/split_v1.json` | Fixed split assignments | Seed/method/freeze marker plus exact IDs per set and split | Initially authored and frozen | Builder, runner, report | Frozen after first API run |
| `data/processed/eval_set_v1.json` | Unified 156-item evaluation input | `item_id`, `gold_set`, `split`, `payload`, and `gold` | `build_eval_set.py` | Runner, evaluator, report | Generated; do not edit by hand |
| `data/processed/MANIFEST.json` | Dataset fingerprints | SHA-256 of three gold files, split, and generated eval set | `build_eval_set.py` | Tests and human integrity checks | Generated |
| `data/processed/.gitkeep` | Empty directory placeholder | Keeps processed directory present | Repository scaffold | Git | Placeholder |
| `data/raw/.gitkeep` | Empty directory placeholder | Keeps raw-data directory present | Repository scaffold | Git | Placeholder |

### `docs/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `docs/PROJECT_GUIDE.md` | This repository guide | Onboarding, script trace, inventories, data, contracts, evaluation, and handoff | This documentation task | New teammates/TAs | Hand-written documentation |
| `docs/ontology/Decision_Mirror_Trait_Ontology.pdf` | Ontology archive | Trait ontology source document | Project source archive | Task docs and human reference | Source archive |
| `docs/ontology/Decision_Mirror_Trait_Ontology_Complete.pdf` | Complete ontology archive | Full ontology, including annotated decision cases | Project source archive | Organic gold provenance | Source archive |
| `docs/proposal/Decision_Mirror_Proposal.pdf` | Proposal archive | Project proposal | Project source archive | Project context | Source archive |
| `docs/proposal/Decision_Mirror_Proposal_main.pdf` | Proposal archive | Main proposal version | Project source archive | Project context | Source archive |
| `docs/proposal/Use_Case.pdf` | Use-case archive | Use-case source document | Project source archive | Project context | Source archive |
| `docs/tasks/task-1-project-analysis/.gitkeep` | Empty task placeholder | Keeps task directory | Repository scaffold | Git | Placeholder |
| `docs/tasks/task-2-trait-ontology/Decision Mirror Trait Ontology.docx` | Task 2 source document | Ontology authoring document | Project source archive | Ontology work | Source archive |
| `docs/tasks/task-2-trait-ontology/Decision_Mirror_Trait_Ontology.pdf` | Task 2 source document | Ontology PDF | Project source archive | Ontology work | Source archive |
| `docs/tasks/task-3-onboarding-quiz/Decision_Mirror_Task_3_Onboarding_Quiz_and_Labeled_Dataset.docx` | Task 3 source document | Quiz and labeling assignment/source | Project source archive | Quiz gold provenance | Source archive |
| `docs/tasks/task-4-llm-extraction/00_team_review.md` | Initial review/planning note | Earlier findings, decisions, open questions, and missing-deliverable status at that time | Hand-written | Historical context | Hand-written; status is historical |
| `docs/tasks/task-4-llm-extraction/01_input_spec.md` | Frozen input contract notes | Fields, model whitelist, quiz mapping, versioning | Hand-written | Implementers and contract tests | Frozen documentation |
| `docs/tasks/task-4-llm-extraction/02_output_spec.md` | Frozen output contract notes | Response semantics, validation rules, envelope, malformed-output policy | Hand-written | Implementers and evaluators | Frozen documentation |
| `docs/tasks/task-4-llm-extraction/03_extraction_prompts.md` | Prompt review notes | Prompt-to-ontology mapping, design decisions, review checklist | Hand-written | Prompt maintainers | Hand-written |
| `docs/tasks/task-4-llm-extraction/04_evaluation_method.md` | Metric/evaluation specification | Metric definitions, denominators, taxonomy, 13 proposed criteria | Hand-written | Evaluator users/reviewers | Hand-written; thresholds pending |
| `docs/tasks/task-4-llm-extraction/05_error_analysis.md` | Dev error analysis | Per-error diagnoses and v2.1 rationale | Hand-written from saved results | Prompt review | Hand-written |
| `docs/tasks/task-4-llm-extraction/06_evaluation_report.md` | Final Task 4 report | Setup, dev/held-out metrics, cases, criteria, conditions and approval line | `build_task4_report.py` | Team and downstream stage | Generated report |
| `docs/tasks/task-4-llm-extraction/07_handoff_to_profile_aggregation.md` | Next-stage handoff | How to interpret scores/confidence/factors and T06 limitations | Hand-written | Profile-aggregation team | Hand-written |
| `docs/tasks/task-4-llm-extraction/TASK4_MANIFEST.json` | Task 4 reproducibility manifest | SHA-256 values for schemas, frozen prompt, datasets, runs, and metrics | `build_task4_report.py` | Reproduction checks | Generated |
| `docs/tasks/task-4-llm-extraction/gold_data.md` | Gold provenance notes | Dataset origins, split design, ambiguity and known issues | Hand-written | Dataset users | Hand-written |
| `docs/tasks/task-4-llm-extraction/how_to_run.md` | Runner instructions | Setup, settings, batch counts, resume/rate-limit and outputs | Hand-written | Operators | Hand-written |
| `docs/tasks/task-4-llm-extraction/source/Decision_Mirror_Task4_Habiba_Final.pdf` | Task 4 source archive | Original Task 4 assignment material | Project source archive | Contract provenance | Source archive |
| `docs/tasks/task-4-llm-extraction/source/Decision_Mirror_Task4_Shams_Amr.docx` | Task 4 source archive | Prompt-related assignment material | Project source archive | Prompt provenance | Source archive |
| `docs/tasks/task-4-llm-extraction/source/Decision_Mirror_Task_4_Team_Assignments.docx` | Task 4 source archive | Team assignment source | Project source archive | Task context | Source archive |

Detailed field rules and evaluation methodology remain in the linked Task 4 documents; this guide summarizes their operation rather than duplicating their full tables.

### `evaluation/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `evaluation/__init__.py` | Python package marker | Evaluation package initialization | Hand-written | Script imports | Hand-written |
| `evaluation/metrics.py` | Metric and error-analysis implementation | `score_band`, `score_metrics`, `spearman_rho`, `quadratic_weighted_kappa`, `normalize_quote`, `is_grounded`, `analyze_items` and helpers | Hand-written | `evaluation/runner.py`, compare/report scripts, tests | Code |
| `evaluation/runner.py` | Offline result writer | `evaluate_run`, run/hash loading, CSV/JSONL output, table and difficult-case renderers | Hand-written | Evaluate/compare/report scripts | Code |
| `evaluation/.gitkeep` | Directory placeholder | Keeps evaluation directory present | Repository scaffold | Git | Placeholder |
| `evaluation/comparisons/v2.0__openai-gpt-oss-120b__all-dev__5825600d__vs__v2.1__openai-gpt-oss-120b__all-dev__5825600d.json` | Paired comparison | Common-item v2.0 vs v2.1 dev deltas, per-trait metrics and paired items | `compare_runs.py` | Prompt decision record | Generated |
| `evaluation/runs/v2.0__openai-gpt-oss-120b__all-dev__5825600d/manifest.json`, `evaluation/runs/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/manifest.json`, `evaluation/runs/v2.1__openai-gpt-oss-120b__all-dev__5825600d/manifest.json` | Run manifests | Prompt/model/eval-set hashes, split, settings, and run metadata | `run_extraction.py` | Resume, evaluation, and report | Generated; preserve |
| `evaluation/runs/v2.0__openai-gpt-oss-120b__all-dev__5825600d/raw_responses.jsonl`, `evaluation/runs/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/raw_responses.jsonl`, `evaluation/runs/v2.1__openai-gpt-oss-120b__all-dev__5825600d/raw_responses.jsonl` | Raw responses | Verbatim model records, one per completed item | `run_extraction.py` | Offline evaluator/report | Frozen evidence; never edit |
| `evaluation/runs/v2.0__openai-gpt-oss-120b__all-dev__5825600d/attempts.log.jsonl`, `evaluation/runs/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/attempts.log.jsonl`, `evaluation/runs/v2.1__openai-gpt-oss-120b__all-dev__5825600d/attempts.log.jsonl` | Attempt logs | Transient API failures, typed status and retry metadata | `run_extraction.py` | Status/resume/audit | Generated; preserve |
| `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/metrics.json`, `evaluation/results/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/metrics.json`, `evaluation/results/v2.1__openai-gpt-oss-120b__all-dev__5825600d/metrics.json` | Metric summaries | Aggregate scores, diagnostics and readiness criteria | `evaluate_run.py` | Report/research | Generated |
| `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/per_item.csv`, `evaluation/results/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/per_item.csv`, `evaluation/results/v2.1__openai-gpt-oss-120b__all-dev__5825600d/per_item.csv` | Per-item tables | Gold/model scores and validation/error status per item | `evaluate_run.py` | Review/analysis | Generated |
| `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/error_log.jsonl`, `evaluation/results/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/error_log.jsonl`, `evaluation/results/v2.1__openai-gpt-oss-120b__all-dev__5825600d/error_log.jsonl` | Error logs | Typed expected/actual findings; an item can have multiple rows | `evaluate_run.py` | Error analysis/report | Generated |
| `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/schema_compliance.json`, `evaluation/results/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/schema_compliance.json`, `evaluation/results/v2.1__openai-gpt-oss-120b__all-dev__5825600d/schema_compliance.json` | Schema-compliance summaries | Overall and per-item strict/schema/semantic/recovery status | `evaluate_run.py` | Compliance review | Generated |
| `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/tables.md`, `evaluation/results/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/tables.md`, `evaluation/results/v2.1__openai-gpt-oss-120b__all-dev__5825600d/tables.md` | Readable metric tables | Formatted metric and readiness tables | `evaluate_run.py` | Human review | Generated |
| `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/difficult_cases.md`, `evaluation/results/v2.0__openai-gpt-oss-120b__all-heldout__5825600d/difficult_cases.md`, `evaluation/results/v2.1__openai-gpt-oss-120b__all-dev__5825600d/difficult_cases.md` | Difficult-case reports | Failures, manual cross-review sample, ambiguous-gold items | `evaluate_run.py` | Human review | Generated |
| `evaluation/runs/` and `evaluation/results/` | Stored run and result collections | The three run IDs are `v2.0__openai-gpt-oss-120b__all-dev__5825600d`, `v2.0__openai-gpt-oss-120b__all-heldout__5825600d`, and `v2.1__openai-gpt-oss-120b__all-dev__5825600d`; file types are detailed above | Runner/evaluator | Reproduction/reporting | Preserve; generated evidence |

### `experiments/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `experiments/legacy/README.md` | Archive note | Says the old experiment is superseded and links review findings | Hand-written | Historical reference | Hand-written |
| `experiments/legacy/ahmed_main_v0.py` | Legacy runner | Earlier, non-resumable Groq runner reading local prompt/data and writing responses | Archived experiment | Historical review only; not official evaluation | Legacy; do not use |

### `prompts/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `prompts/extraction/registry.json` | Prompt registry | v1.x legacy, v2.0 frozen, v2.1 draft; file hashes/status/parentage/metadata | Hand-maintained | `load_prompt()` and leakage tests | Update only for a new prompt version |
| `prompts/extraction/extraction_v2.0.md` | Selected frozen prompt | Nine sections: role/boundaries; ontology/scoring and T01–T06; trait/preference/situation/constraint; evidence/confidence; nulls; source handling; status/output; illustrative examples; final self-check | Hand-written; registered | Extraction runner | Frozen; never edit in place |
| `prompts/extraction/extraction_v2.1.md` | Rejected candidate prompt | Draft revision clarifying evidence for situational-factor causality | Hand-written; registered | Dev comparison only | Draft; do not use as final |
| `prompts/extraction/CHANGELOG.md` | Version history | Why v1.x were archived, v2.0 frozen, and v2.1 not selected | Hand-written | Prompt maintainers/reviewers | Hand-written |
| `prompts/extraction/legacy/README.md` | Legacy archive note | States v1.x are provenance only and not official-evaluation prompts | Hand-written | Historical reference | Hand-written |
| `prompts/extraction/legacy/v1.0.md`, `prompts/extraction/legacy/v1.1.md`, `prompts/extraction/legacy/v1.2.md`, `prompts/extraction/legacy/v1.3.md` | Archived prompts | Four earlier prompt versions, preserved with registry hashes | Archived source versions | Prompt history only; loader requires explicit legacy opt-in | Legacy; do not edit |

### `schemas/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `schemas/extraction_input.schema.json` | Input JSON Schema | Required IDs/source/text/ontology; optional timestamp/language/context; rejects unknown fields | Hand-written contract | `payloads.py`, tests | Frozen contract |
| `schemas/extraction_output.schema.json` | Model response JSON Schema | Exact response fields, six ordered trait slots, score/factor constraints | Hand-written contract | `validation.py`, tests | Frozen contract |
| `schemas/extraction_result.schema.json` | Pipeline envelope JSON Schema | Result metadata, pipeline-only error status, validation summary and trait envelope | Hand-written contract | Contract tests; not currently assembled by the extraction runner | Frozen contract |
| `schemas/examples/valid/fully_scored_narrative.json`, `schemas/examples/valid/insufficient_evidence_short_text.json`, `schemas/examples/valid/multi_trait_narrative.json`, `schemas/examples/valid/quiz_success_off_target_null.json`, `schemas/examples/valid/situational_constraint.json`, `schemas/examples/valid/t06_null_without_history.json` | Valid contract fixtures | Six examples covering scored, null, quiz, context, and T06 cases | Hand-written | `test_contract.py` | Hand-written fixtures |
| `schemas/examples/invalid/duplicate_trait.json`, `schemas/examples/invalid/evidence_is_string.json`, `schemas/examples/invalid/extra_top_level_field.json`, `schemas/examples/invalid/five_traits.json`, `schemas/examples/invalid/markdown_fenced_json.json`, `schemas/examples/invalid/model_emits_error_status.json`, `schemas/examples/invalid/null_score_nonzero_confidence.json`, `schemas/examples/invalid/null_score_with_evidence.json`, `schemas/examples/invalid/plain_text_response.json`, `schemas/examples/invalid/score_above_one.json`, `schemas/examples/invalid/score_string_null.json`, `schemas/examples/invalid/success_all_null_scores.json`, `schemas/examples/invalid/t06_scored_without_history.json`, `schemas/examples/invalid/wrong_trait_name_for_id.json`, `schemas/examples/invalid/wrong_trait_order.json` | Invalid contract fixtures | Fifteen malformed/schema/semantic counterexamples | Hand-written | `test_contract.py` | Hand-written fixtures |

### `scripts/`

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `scripts/build_eval_set.py` | Dataset builder | Reads gold/split, maps payloads, writes eval set and manifest | Hand-written | Dataset maintenance | Code |
| `scripts/run_extraction.py` | Resumable API runner | Flags, manifest checks, batch/retry/resume, raw response writes | Hand-written | Extraction operation | Code |
| `scripts/evaluate_run.py` | Offline CLI | Loads one run and writes its result files | Hand-written | Evaluation | Code |
| `scripts/compare_runs.py` | Offline paired comparison | Evaluates two runs and writes common-item comparison JSON | Hand-written | Prompt comparisons | Code |
| `scripts/build_task4_report.py` | Report generator | Verifies frozen artifacts and renders report + artifact manifest | Hand-written | Final report reproduction | Code |
| `scripts/update_file_structure.py` | Tree generator | Recursively renders repository entries into `file_structure.txt` | Hand-written | Repository housekeeping | Code |

### `src/`

| Path | What it is | Main functions/classes and purpose | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `src/decision_mirror/__init__.py` | Package marker | Initializes top-level package | Hand-written | Python imports | Code |
| `src/decision_mirror/extraction/__init__.py` | Extraction package marker | Initializes extraction package | Hand-written | Python imports | Code |
| `src/decision_mirror/extraction/payloads.py` | Request payload helpers | `build_quiz_payload()` maps scenario/selected answer; `build_model_request()` validates and strips application-only fields | Hand-written | Builder, pipeline, tests | Code |
| `src/decision_mirror/extraction/prompt_loader.py` | Prompt registry loader | `load_prompt()` resolves registry entry, enforces legacy opt-in, checks frozen hash | Hand-written | Runner, tests | Code |
| `src/decision_mirror/extraction/validation.py` | Output validation | `ValidationOutcome`; strict JSON duplicate/nonfinite checks; `classify_response()`, semantic checks, recovery diagnostic; `classify_api_error()` | Hand-written | Runner, evaluator, tests | Code |
| `src/decision_mirror/extraction/pipeline.py` | Single-item call flow | `run_item()` builds whitelisted request, hashes request+prompt, calls client, returns raw completion metadata | Hand-written | Extraction runner | Code |
| `src/decision_mirror/extraction/llm_client.py` | LLM client abstraction | `Completion`, `LLMClient`, `GroqClient`, and test `MockClient`; reads API key and calls Groq | Hand-written | Runner/tests | Code |
| `src/decision_mirror/quiz/__init__.py`, `src/decision_mirror/profiling/__init__.py`, `src/decision_mirror/retrieval/__init__.py`, `src/decision_mirror/advisory/__init__.py`, `src/decision_mirror/storage/__init__.py`, `src/decision_mirror/common/__init__.py` | Placeholder packages | Only package initialization; no feature functions/classes | Scaffold | Future work | Empty placeholders |

### `tests/`

| Path | What it is | What it protects |
|---|---|---|
| `tests/.gitkeep` | Directory placeholder | Keeps test directory present |
| `tests/test_contract.py` | Contract and fixture tests | Draft-07 schemas, valid/invalid examples, semantic rules, payload allowlist, malformed output classification |
| `tests/test_eval_set.py` | Eval-set tests | Full gold-set coverage, schema-valid payloads, quiz leakage exclusion, deterministic eval set and manifest hashes |
| `tests/test_evaluation.py` | Metrics/evaluation tests | Metric correctness, T06 violations, recovered JSON policy, band boundaries, evidence normalization, ambiguity handling, raw-response immutability, paired comparisons |
| `tests/test_prompt_leakage.py` | Prompt safety/regression tests | No gold text/IDs in draft/frozen prompts; required traits/statuses/bands remain represented |
| `tests/test_prompt_loader.py` | Prompt-loader tests | Registry loading/hash return, frozen hash mismatch, legacy opt-in, unknown versions |
| `tests/test_runner.py` | Runner/client tests | Batch resume, interruption, rate limits, malformed final outputs, manifest mismatch, API-key non-persistence, status/dry-run, verbatim response/reasoning, SDK parameter checks |
| `tests/test_split.py` | Split tests | Seed-42 reproducibility, whole quiz-question grouping and stratification, organic holdout selection, edge dev-only rule |

### Root files

| Path | What it is | What is inside | Produced by | Used by | Editable? |
|---|---|---|---|---|---|
| `.vscode/settings.json` | Workspace editor setting | Enables VS Code terminal environment-file use | Hand-written | VS Code workspace | Hand-written |
| `README.md` | Repository landing page | Setup, commands, Task 4 status, links to major docs and data | Hand-written | New contributors | Hand-written |
| `.env.example` | Safe environment template | Variable names and defaults for Groq/model settings; placeholder API-key line only | Hand-written | Local setup; copied to `.env` | Hand-written template; no real secret |
| `.gitignore` | Git ignore rules | Ignores venv, `.env`, caches, bytecode, and egg-info | Hand-written | Git | Hand-written |
| `pyproject.toml` | Python project config | Package metadata, src layout, pytest import paths | Hand-written | pip/build/pytest | Hand-written |
| `requirements.txt` | Pinned dependencies | Groq, HTTPX, jsonschema, python-dotenv, pytest | Hand-written | Environment setup | Hand-written |
| `file_structure.txt` | Generated repository tree | Current filesystem tree excluding configured cache/venv paths | `update_file_structure.py` | Repository orientation | Generated |

## 7. The data in detail

### Gold sources and record shape

- **Quiz:** `data/gold/quiz_gold_v1.0.json` is the supplied Task 3 set: 25 questions × five answer options = 125 records. A record includes `record_id`, source/question/trait identifiers, scenario, selected answer text, `gold_value`, evidence, confidence, situational-factor and context fields. The gold target is one trait per record. Confidence is uniformly 0.70; the source materials record a 0.70/0.90 discrepancy.
- **Organic:** `data/gold/organic_gold_v1.0.json` has 20 transcribed narratives from §9 of `docs/ontology/Decision_Mirror_Trait_Ontology_Complete.pdf`. Each record includes `record_id`, `decision_text`, `gold_traits` (T01–T06 values/confidence), `gold_evidence`, gold factor, an edge-case reference, and ambiguity flag/note. Dashes/null source values remain null; some retain nonzero confidence.
- **Edge cases:** `data/gold/edge_cases_v1.0.json` has 11 self-authored behavior tests: insufficient evidence, constraints, conflicting motivations, emotional/analytical cues, contradictions, multi-trait signals, unsupported history claims, long narratives, and embedded instruction attempts. Its `expected` object describes behaviors (for example expected status, null/non-null traits, factor presence, confidence ceiling), not numeric gold scores.

### Split and eval-set construction

`data/processed/split_v1.json` stores exact IDs and seed 42. For quiz records, two of each trait's five question IDs are held out; all five answer records for each question stay together, giving 75 dev and 50 held-out. Organic assignment holds out two records linked to ontology §10 edge cases plus four without such references, giving 14 dev and 6 held-out. All 11 self-authored edge cases are dev-only. The exact assignments, not a fresh sample, are used by the runner.

`data/processed/eval_set_v1.json` has 156 items (125 quiz, 20 organic, 11 edge). Each item has `item_id`, `gold_set`, `split`, `payload`, and `gold`. Quiz gold has a `target_trait`, six `traits` slots, optional factor, and ambiguity marker; organic gold has trait map/factor/ambiguity; edge gold has null trait slots plus `expected`.

The builder creates quiz model-facing text as `Scenario: ...` plus `Selected answer: ...`; organic and edge model-facing text comes from the narrative. It retains gold in the eval record for local scoring, but `build_model_request()` only sends allowed input fields. Thus the model sees the decision ID, source type, decision text, ontology version, language, and only explicitly supplied history. It does **not** receive gold values, evidence annotations, target trait, answer-choice list, `user_id`, timestamp, or quiz `question_id`. Other quiz options are not copied into the selected-answer narrative.

`data/processed/MANIFEST.json` fingerprints each gold file, the frozen split, and the generated eval set using SHA-256. `data/gold/CHECKSUMS.txt` separately records the quiz gold digest. `docs/tasks/task-4-llm-extraction/TASK4_MANIFEST.json` records SHA-256 values for the Task 4 contracts, prompt, data, runs, and metrics.

## 8. Contracts

The authoritative input/output field details are in [the input spec](tasks/task-4-llm-extraction/01_input_spec.md), [the output spec](tasks/task-4-llm-extraction/02_output_spec.md), and the three schemas in `schemas/`.

- **Input:** a strict object with `decision_id`, `user_id`, `source_type`, `decision_text`, and `ontology_version`; optional timestamp, language, and context. Only `decision_log` / `onboarding_quiz` and ontology `v1.0` are accepted. Unknown properties are rejected. Decision text is nonblank and at most 4000 characters.
- **Model input whitelist:** `payloads.build_model_request()` validates the full input then keeps `decision_id`, `source_type`, `decision_text`, `ontology_version`, and `language`; it only forwards `context.history` if present. In ordinary Task 4 payloads history is absent.
- **Model output:** JSON with the matching `decision_id`, status `success` or `insufficient_evidence`, and exactly six trait objects in T01–T06 order. Trait names are fixed; each object includes a score/null, confidence, evidence array, situational factor/null, and context notes.
- **Status:** `success` iff at least one score is non-null; `insufficient_evidence` iff all are null. Enforced by semantic checks in `_validate_semantics()` in `src/decision_mirror/extraction/validation.py`.
- **Null/confidence/evidence:** a null score requires confidence exactly `0.0` and empty evidence; scored traits require evidence; null T01–T05 require explanatory notes. These semantic checks are in `validation.py`, and related constraints also appear in `schemas/extraction_output.schema.json`. T06 must be null when history is absent/empty.
- **Evidence grounding:** evidence is intended to be an exact quote. The validator warns (does not reject) when whitespace/quote-normalized evidence is missing from input; the evaluation grounding metric uses `evaluation.metrics.is_grounded()`.
- **Situational factor:** null or an object with `category` and `description`; categories are `financial_dependency`, `family_pressure`, `external_deadline`, `external_constraint`, `limited_alternatives`, `social_influence`, `low_stakes`, or `other`. It belongs to each trait output rather than a top-level response field.
- **Pipeline versions and result envelope:** `schemas/extraction_result.schema.json` defines an envelope where model version, prompt version/hash, error, and validation are pipeline-owned—not LLM-generated. In the actual runner, `run_item()` returns raw completion data and `run_extraction.py` adds model/prompt metadata to that stored record; the current runner does not construct or validate the full result envelope.
- **Malformed output:** `classify_response()` distinguishes `empty_response`, `not_json`, `schema_violation`, and `semantic_violation`; API errors are classified separately. Duplicate JSON keys and non-finite numeric values are rejected. A lenient recovery pass only marks whether fenced/prose-wrapped JSON could be recovered; it never substitutes recovered text. Evaluation records the invalid first response. The runner persists malformed completions as final raw responses and does not retry them.

## 9. Prompts

`prompts/extraction/registry.json` is the source of version, file, hash, status, parent and summary. `load_prompt()` refuses unknown versions and legacy prompts unless explicitly opted in. It calculates a SHA-256 digest for every loaded file and enforces the registered digest only when status is `frozen`. Never edit a frozen prompt in place; add a new version and changelog entry.

- **v2.0:** frozen, parent v1.3, selected for final evaluation. Registered SHA-256: `6f93b33da4bf2193641bb47156b1ca090a84f86f718e69085513aae4e6d280d7`.
- **v2.1:** draft, parent v2.0. It clarified causal evidence for factor categories and constraints; the dev organic factor-recall result was 66.7%, below the proposed 80% threshold, so it was not selected. Missed eligible factor ORG11; ORG05 was also missed but ambiguous and excluded from headline recall.
- **v1.0–v1.3:** legacy prompt files in `prompts/extraction/legacy/`; retained for provenance, not official evaluation. The loader requires `allow_legacy=True`.

The v2.0 file sections are: (1) role and boundaries; (2) ontology and score direction for T01–T06; (3) trait vs preference vs situation vs constraint; (4) evidence tiers and confidence; (5) null scores; (6) source handling; (7) status/output shape; (8) self-authored examples; (9) final self-check. Design rationale and mapping to ontology are documented in [the prompt review](tasks/task-4-llm-extraction/03_extraction_prompts.md).

## 10. Evaluation explained

`evaluation/runner.py` matches raw responses to the eval set by `item_id`; `evaluation/metrics.py` calculates metrics. Partial runs include only responses actually present. Headline score metrics pair numeric gold with numeric predictions; misses and coverage are reported separately.

### Metrics and formulas

The five half-open score bands are `[0.0,0.2)`, `[0.2,0.4)`, `[0.4,0.6)`, `[0.6,0.8)`, `[0.8,1.0]`. `score_band()` maps a score using `min(int(score * 5), 4)`.

| Metric | Plain-language formula | Implementation |
|---|---|---|
| MAE | `sum(abs(gold - prediction)) / paired numeric count` | `score_metrics()` |
| Exact-band accuracy | Same-band pairs / paired numeric count | `score_metrics()` |
| Within-one-band rate | Pairs no more than one band apart / pairs | `score_metrics()` |
| Quadratic-weighted kappa | `1 - observed weighted band disagreement / expected disagreement`; squared band distance weighted by 1/16 | `quadratic_weighted_kappa()` |
| Spearman rho | Pearson correlation of average ranks (ties get average rank) | `spearman_rho()` and helpers |
| Direction accuracy | Same side of 0.5; excludes gold exactly 0.5; predicted 0.5 counts as lower side | `score_metrics()` |
| Polarity inversion | Opposite side of 0.5 **and** absolute score error > 0.2; rate denominator is paired numeric scores | `score_metrics()` |
| Bootstrap 95% interval | Percentile interval over 2,000 paired-record resamples, seed 42; undefined correlations omitted | `_bootstrap_ci()` |
| Target non-null rate | Non-null quiz target predictions / quiz target items present | `analyze_items()` |
| Missed-signal rate | Gold-non-null organic T01–T05 traits predicted null / gold-non-null traits | `analyze_items()` |
| Unsupported-inference rate | Non-null prediction on gold-null organic T01–T05 / gold-null opportunities | `analyze_items()` |
| Status accuracy | Model status matching status derived from any numeric gold trait | `_expected_status()` and `analyze_items()` |
| Factor precision/recall | Per-decision factor TP/(TP+FP) and TP/(TP+FN); category agreement checks whether predicted categories include gold category | `analyze_items()` |
| Evidence grounding | Grounded returned quotes / all returned quotes; empty evidence adds no quote | `normalize_quote()`, `is_grounded()`, `analyze_items()` |
| Confidence metrics | Distribution across non-null scored traits; organic confidence MAE only for unambiguous numeric gold with both confidence values | `analyze_items()` |
| Edge pass rate | Passed defined qualitative expected checks / all defined checks | `_expected_edge_checks()` and `analyze_items()` |
| Evidence token-overlap F1 | Multiset token-overlap F1 against organic annotation evidence; report-only, not a source-grounding metric | `_token_f1()` |

The evidence normalizer has a post-hoc fix: after the initial development results, it was changed to accept balanced surrounding quote delimiters in addition to collapsing whitespace, normalizing typographic quotes, and case-folding. The corrected evaluator was applied to all saved runs, with a regression test. `validation.py` independently emits an `evidence_not_grounded` warning using whitespace and quote normalization; it does not reject a response for that warning.

### Error taxonomy

`error_log.jsonl` can contain multiple rows per item. Severity/category rules are specified in [the evaluation method](tasks/task-4-llm-extraction/04_evaluation_method.md):

| Category | Meaning | Severity in the evaluation method |
|---|---|---|
| `malformed_output` | Empty/non-JSON output or schema/semantic validation failure. | Critical |
| `missed_signal` | Organic gold numeric trait is null in the model output. | Major |
| `unsupported_inference` | Organic T01–T05 gold-null trait is scored. | Major |
| `polarity_inversion` | Prediction is across 0.5 by more than 0.2. | Critical |
| `score_deviation` | Numeric prediction differs by one or more bands. | Minor (1), major (2), critical (3+) |
| `evidence_not_grounded` | Evidence quote does not occur in normalized input text. | Major |
| `context_confusion` | Factor missed, hallucinated, miscategorized, or constraint treated as trait evidence. | Major |
| `confidence_miscalibration` | Confidence ≥0.8 with score error of at least two bands. | Major |
| `status_error` | Model status differs from status implied by gold. | Major |
| `t06_violation` | T06 is non-null without history. | Major |
| `edge_case_failure` | A qualitative expected behavior check fails. | Major |
| `needs_manual_review` | Deterministic sample of exact-band-correct items for human evidence-support review; not an automated error finding. | Review |

### The 13 proposed readiness criteria

They are proposed and **pending team-lead approval**. A missing denominator is `not_applicable`, not a pass.

| Criterion | Threshold |
|---|---:|
| Strict schema-valid rate | ≥95% |
| Schema-valid or recovered diagnostic rate | ≥99% (recovered still means invalid output) |
| Quiz target non-null rate | ≥90% |
| Quiz exact-band accuracy | ≥60% |
| Quiz within-one-band rate | ≥90% |
| Quiz MAE | ≤0.15 |
| Quiz direction accuracy | ≥90% |
| Quiz Spearman rho | ≥0.80 |
| Quiz polarity-inversion rate | ≤2% |
| Evidence grounding | ≥98% |
| T06 violations | 0 |
| Edge-case pass rate | ≥80% |
| Organic situational-factor recall | ≥80% |

Organic `ambiguous_gold` records are omitted from headline organic scoring, missed/unsupported inference, status, factor detection, and confidence metrics. Their available numeric score comparisons are reported separately under `ambiguous_gold_score_metrics`; they are not discarded from the dataset. T06 is excluded from organic score metrics because scores are calculated for T01–T05 only, and the output contract requires null T06 without history.

## 11. Results snapshot

Headline figures below were read from the stored `metrics.json` files, not transcribed from memory:

| v2.0 metric | Dev (`v2.0__openai-gpt-oss-120b__all-dev__5825600d`) | Held-out (`v2.0__openai-gpt-oss-120b__all-heldout__5825600d`) |
|---|---:|---:|
| Responses | 100 | 56 |
| Quiz numeric target pairs / target items | 73 / 75 | 46 / 50 |
| Quiz target non-null rate | 97.3% | 92.0% |
| Quiz exact-band accuracy | 67.1% | 65.2% |
| Quiz MAE | 0.073 | 0.069 |
| Quiz within-one-band rate | 100% | 100% |
| Organic situational-factor recall | 100% (3 TP, 0 FN) | 100% (1 TP, 0 FN) |
| Organic factor category agreement | 0% | 100% |
| Edge checks | 39/47 = 83.0% | Not applicable; no held-out edge cases |
| Strict schema validity | 100% | 100% |
| Evidence grounding | 100% (168/168 quotes) | 100% (93/93 quotes) |

Known weaknesses matter more than the headline alone: held-out organic recall is based on only six organic records and one positive factor; factor category agreement is 0% on dev; quiz scores compress toward inner bands; quiz tasks are short/templated; T04 exact-band accuracy is only 33.3% held-out (MAE 0.128); model confidence is not calibrated; and human evidence cross-review is outstanding. The complete result tables and caveats are in the [Task 4 evaluation report](tasks/task-4-llm-extraction/06_evaluation_report.md).

## 12. Invariants and do not do this

1. Never edit gold files, the three checked-in `raw_responses.jsonl` files listed in the inventory, frozen prompts, or `data/processed/split_v1.json` after runs have begun.
2. Never use a non-frozen prompt for held-out evaluation. The runner currently does not enforce this; check registry status yourself.
3. Do not resume a run after changing the model, prompt/version hash, evaluation set, split, batch size, or other manifest-checked settings. Use a new run instead.
4. Do not copy gold fields into model-facing payloads, prompt text, or API requests.
5. Do not treat recovered JSON as valid output, model confidence as calibrated probability, or the held-out organic estimate as statistically stable.
6. Do not assign T06 from one narrative or a claim such as “I always do this”; Task 4 supplies no longitudinal history.
7. Do not turn situational factors into stable user traits. The downstream handoff recommends an explicit, validated relative weighting policy.

## 13. How-to recipes

### Run the next 10 items in a dev run

Preview first, then run the same command again for successive pending batches. This command makes API calls when items are pending:

```powershell
.\.venv\Scripts\python.exe scripts\run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split dev --batch-size 10 --dry-run
.\.venv\Scripts\python.exe scripts\run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split dev --batch-size 10
```

Repeat the second command until `RUN COMPLETE`; completed IDs are skipped.

### Check run status

```powershell
.\.venv\Scripts\python.exe scripts\run_extraction.py --prompt v2.0 --model openai/gpt-oss-120b --set all --split all --status
```

`--status` lists all run folders and does not instantiate the API client.

### Evaluate a saved run

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-dev__5825600d
```

This is offline and refreshes the six files in that run's results folder.

### Compare two prompt versions

First obtain saved dev runs for both versions; do not use held-out to iterate. Then compare:

```powershell
.\.venv\Scripts\python.exe scripts\compare_runs.py v2.0__openai-gpt-oss-120b__all-dev__5825600d v2.1__openai-gpt-oss-120b__all-dev__5825600d
```

Comparison/evaluation makes no API calls, but it regenerates the two result folders and writes a paired comparison JSON.

### Add a prompt version

1. Create a new prompt file; do not edit `extraction_v2.0.md` in place.
2. Add a registry entry with unique version, parent, file path, status, date, summary, and the file's byte-level SHA-256; document the change in `prompts/extraction/CHANGELOG.md`.
3. Run `python -m pytest -q tests/test_prompt_loader.py tests/test_prompt_leakage.py` and review output/ontology alignment. The leakage test inspects every registry entry with `draft` or `frozen` status.
4. Run dev evaluation, review errors and cross-review sample; only after approval should a candidate be frozen and considered for held-out evaluation.

### Add a new gold set

Do not modify existing versioned gold or the frozen split. Add a separately versioned source file and provenance note; define its payload and annotation shape; update `scripts/build_eval_set.py` to map it (the current builder explicitly enumerates the three current sets); add a new split/eval-set version and manifest rather than silently changing v1; add schema/leakage/determinism tests; and approve/freeze the new split before making API calls. **UNVERIFIED:** no general plugin mechanism or automated new-set migration exists; this is a repository-change recipe, not an already-supported command.

### Reproduce the final report from a fresh clone

The committed runs permit offline reproduction; this sequence uses no API key. Use PowerShell's venv Python directly if activation is blocked.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-dev__5825600d
.\.venv\Scripts\python.exe scripts\evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-heldout__5825600d
.\.venv\Scripts\python.exe scripts\build_task4_report.py
```

The report builder regenerates the report date and `TASK4_MANIFEST.json`; compare regenerated metrics with the committed values in the manifest before relying on the result.

## 14. FAQ and troubleshooting

| Symptom | What to do |
|---|---|
| Quota/rate-limit stop | Exit code **3** means 429 persisted through three attempts. Wait for quota, rerun the identical command, and let the runner resume the pending item. Completed responses remain saved. |
| PowerShell says scripts are disabled | Run `.\.venv\Scripts\python.exe -m pytest -q` (or invoke another command with that interpreter) rather than `Activate.ps1`. |
| Frozen prompt SHA-256 mismatch | Do not edit the prompt or registry hash to silence it. Restore the exact registered prompt or create a new version; the loader intentionally refuses altered frozen bytes. |
| Resume manifest mismatch | Keep all recorded settings the same or pass `--new-run`; that creates a timestamp-suffixed run and preserves prior files. |
| Evaluation-set hash mismatch | Restore the eval set associated with that run. Do not regenerate or modify the split/eval set to force an old run to evaluate. |
| Missing API key | Review `.env.example`, create local `.env` from it, and add your own `GROQ_API_KEY` without printing or committing the secret. Offline evaluation does not need it. |
| `--help` appears to execute work | `build_eval_set.py`, `build_task4_report.py`, and `update_file_structure.py` have no CLI parser; do not pass `--help` to them unless you intend their normal file-writing action. |

## 15. Open items and limitations

- Team-lead approval of the proposed readiness criteria and report is pending; the report's approval line is blank.
- Human evidence-support cross-review remains outstanding. The deterministic `needs_manual_review` sample is a queue, not a finding.
- Quiz confidence gold has a documented 0.70/0.90 source inconsistency; organic gold is only 20 records; edge checks are self-authored; and the held-out organic split is only six records.
- `docs/tasks/task-4-llm-extraction/07_handoff_to_profile_aggregation.md` expects downstream aggregation to keep T01–T05 evidence distinct from context, treat confidence as relative evidence weight only after defining policy, down-weight contextual observations via a documented policy, and leave T06 null until a future history-capable contract.
- **Documentation/code inconsistencies found (not changed):** the output spec describes a pipeline result envelope with injected version fields, but the current extraction runner stores raw completion records with model/prompt metadata and does not build/validate that envelope; the runner permits a registered draft prompt on `--split heldout` despite docs saying held-out must use a frozen prompt; and `extraction_v2.1.md`'s title still says “System Prompt v2.0” although the registry identifies it as v2.1. The initial `00_team_review.md` also describes missing deliverables from an earlier planning state; the later evaluation report documents those deliverables as completed.
- **UNVERIFIED:** the Task 4 source archive's original assignment requirements were not independently reconciled against every final implementation detail; this guide relies on current repository code and checked-in Task 4 Markdown/specifications.
