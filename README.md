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

## Task 4 status

- [x] Prompt 1: environment, scaffold, source archive, and team review.
- [x] Prompt 2: frozen input/output contracts, validators, examples, and tests.
