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

## Task 4 status

- [x] Prompt 1: environment, scaffold, source archive, and team review.
- [ ] Later prompts: not yet completed.
