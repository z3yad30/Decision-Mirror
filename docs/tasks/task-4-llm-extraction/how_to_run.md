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

Run the development split first, then held-out. Repeat each command unchanged
until it prints `RUN COMPLETE`:

```powershell
python scripts/run_extraction.py --prompt v2.0 --set all --split dev
python scripts/run_extraction.py --prompt v2.0 --set all --split heldout
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
`raw_responses.jsonl`, and `attempts.log.jsonl`. The manifest records the prompt
and evaluation-set hashes plus model settings. Response records preserve the
verbatim message content; reasoning text, when returned separately by the
SDK, is stored in its own field. Transient failures are only written to the
attempt log.
