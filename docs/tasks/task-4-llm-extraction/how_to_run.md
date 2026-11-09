# Running the resumable extraction runner

Run commands from the repository root. The runner sends only the contract's
whitelisted model payload; gold labels stay in the local evaluation set and are
never included in requests.

## Setup

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Add `GROQ_API_KEY` to the untracked `.env` file. The runner reads model settings
from `.env` when present:

| Variable | Default | Meaning |
|---|---:|---|
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Model identifier (overridden by `--model`) |
| `GROQ_TEMPERATURE` | `0` | Sampling temperature |
| `GROQ_MAX_TOKENS` | `4096` | Sent as Groq's `max_completion_tokens` |
| `GROQ_REASONING_EFFORT` | `medium` | Reasoning effort |
| `REQUEST_DELAY_SECONDS` | `3` | Delay between items |

The runner processes at most 10 items per invocation. It writes one synced JSONL
record per completion, including malformed completions, so a finished item is
never requested again. Transient API failures are recorded separately and
remain pending.

## Full protocol

Run the current draft on the development split only. Repeat the command
unchanged until it prints `RUN COMPLETE`. Do not run held-out until the final
prompt version is confirmed and frozen. The runner enforces registry status
`frozen` for both `--split heldout` and `--split all`; a draft prompt is rejected
with exit code 2 before dry-run or new-run processing. `--status` remains
available for existing runs.

```powershell
python scripts/run_extraction.py --prompt v2.1 --model openai/gpt-oss-120b --set all --split dev
```

Progress is persistent across invocations. For the current evaluation set, the
work is:

| Set | Dev items / runs | Held-out items / runs |
|---|---:|---:|
| Quiz | 75 / 8 | 50 / 5 |
| Organic | 14 / 2 | 6 / 1 |
| Edge | 11 / 2 | 0 / 0 |
| All | 100 / 10 | 56 / 6 |

Run counts are ceiling(item count / 10). If running quiz by itself across both
splits, 125 items require 13 invocations. An empty set/split selection (such
as edge held-out) has no items to process.

To preview the next batch without making an API request:

```powershell
python scripts/run_extraction.py --prompt v2.0 --set all --split dev --dry-run
```

To view progress for all run folders without making an API request:

```powershell
python scripts/run_extraction.py --prompt v2.0 --set all --split all --status
```

If a 429 persists through three attempts, the runner saves completed work,
prints `Quota/rate limit reached after N items; run again later`, and exits
with code 3. Wait for quota to recover, then repeat the same command; the
pending item is selected first. For immediate retries of server errors and
connection timeouts within the same invocation, add `--retry-api-failures`.
Completed malformed responses are final results and are not retried.

Use `--model MODEL_ID` to choose a different model. `--batch-size` can be from
1 to 10. `--new-run` preserves existing data and creates a timestamp-suffixed
run folder; without it, the runner resumes the deterministic run identity.
There is no reset command. Removing a run folder is a manual operation.

## Output files

Each run is stored under `evaluation/runs/<run_id>/` with a `manifest.json`,
`raw_responses.jsonl`, and `attempts.log.jsonl`. New runs additionally write
schema-shaped pipeline result envelopes to `result_envelopes.jsonl`, including
explicit error envelopes for API failures. This additional file is not part of
the resume manifest check. The raw-response record format remains unchanged:
response records preserve verbatim message content; reasoning text, when
returned separately by the SDK, is stored in its own field. Transient API
failures remain recorded in the attempt log.

The envelope follows the existing
`schemas/extraction_result.schema.json`: the pipeline injects model version,
prompt version and hash, validation summary, and pipeline-only `error` status
for API or output-format failures. The historical runs are not backfilled.
An API-error envelope does not mark its decision as complete; a resumed run can
append a later envelope for the same `decision_id`. Multiple rows per decision
are therefore valid, and the last row for each `decision_id` is the current
envelope. For completed model responses, the raw record is synced before
classification or envelope construction; an envelope-generation failure is
typed and recorded in `attempts.log.jsonl` without discarding that raw record.

## Offline post-hoc supplementary analyses

After saved runs have been evaluated, the supplementary command makes no API
calls and does not rewrite `metrics.json` or `tables.md`:

```powershell
python scripts/evaluate_supplementary.py
```

It writes `supplementary_metrics.json` and `supplementary.md` beside the
existing results for the three saved runs. These files are labeled
**post-hoc: added after dev and held-out results were seen**. The report
includes quiz non-target scoring as a descriptive rate (not an error rate),
factor precision/recall/category agreement, the recovered original quote
normalizer comparison, and question-cluster bootstrap results. Existing
held-out evaluations of a prompt not registered as `frozen` emit a loud
warning when run through `evaluate_run.py`.
