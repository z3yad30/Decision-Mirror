from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from decision_mirror.extraction.llm_client import MockClient

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "run_extraction", ROOT / "scripts" / "run_extraction.py"
)
assert _SPEC is not None and _SPEC.loader is not None
runner = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(runner)


def _configure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    items = json.loads(
        (ROOT / "data" / "processed" / "eval_set_v1.json").read_text(
            encoding="utf-8"
        )
    )
    eval_path = tmp_path / "eval_set.json"
    eval_path.write_text(json.dumps(items), encoding="utf-8")
    monkeypatch.setattr(runner, "EVAL_PATH", eval_path)
    monkeypatch.setattr(runner, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setenv("REQUEST_DELAY_SECONDS", "0")
    monkeypatch.setenv("GROQ_API_KEY", "secret-test-key-must-not-be-written")
    return items


def _invoke(client: MockClient, **overrides) -> int:
    options = {
        "prompt_version": "v2.0",
        "gold_set": "quiz",
        "split": "dev",
        "client": client,
        "sleep": lambda _: None,
    }
    options.update(overrides)
    return runner.run_invocation(**options)


def _run_folder() -> Path:
    return next(runner.RUNS_DIR.iterdir())


def _records(run_folder: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in (run_folder / "raw_responses.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]


def test_batches_resume_without_skips_or_duplicates_and_completed_run_is_noop(
    tmp_path, monkeypatch, capsys
):
    _configure(tmp_path, monkeypatch)
    client = MockClient()

    assert _invoke(client) == 0
    run_folder = _run_folder()
    first = _records(run_folder)
    assert len(first) == 10
    assert len({row["item_id"] for row in first}) == 10

    assert _invoke(client) == 0
    second = _records(run_folder)
    assert len(second) == 20
    assert {row["item_id"] for row in first}.isdisjoint(
        row["item_id"] for row in second[10:]
    )

    items = json.loads(runner.EVAL_PATH.read_text(encoding="utf-8"))
    selected = runner._select_items(items, "quiz", "dev")
    while len(_records(run_folder)) < len(selected):
        assert _invoke(client) == 0

    finished = _records(run_folder)
    assert len(finished) == len(selected)
    assert [row["item_id"] for row in finished] == [
        item["item_id"] for item in selected
    ]
    captured_before = len(client.captured_requests)
    assert _invoke(client) == 0
    assert len(client.captured_requests) == captured_before
    assert "RUN COMPLETE" in capsys.readouterr().out


def test_interrupted_batch_resumes_after_saved_items(tmp_path, monkeypatch):
    items = _configure(tmp_path, monkeypatch)

    class CrashAfterFour(MockClient):
        def complete(self, prompt, request):
            if len(self.captured_requests) >= 4:
                raise RuntimeError("simulated process interruption")
            return super().complete(prompt, request)

    with pytest.raises(RuntimeError, match="simulated process interruption"):
        _invoke(CrashAfterFour())

    run_folder = _run_folder()
    saved = _records(run_folder)
    assert len(saved) == 4
    assert [row["item_id"] for row in saved] == [
        item["item_id"] for item in runner._select_items(items, "quiz", "dev")[:4]
    ]

    client = MockClient()
    assert _invoke(client) == 0
    records = _records(run_folder)
    assert len(records) == 14
    assert len({row["item_id"] for row in records}) == 14


def test_rate_limit_stops_cleanly_and_pending_item_resumes(
    tmp_path, monkeypatch, capsys
):
    _configure(tmp_path, monkeypatch)
    client = MockClient(mode="rate_limit")

    assert _invoke(client) == 3
    run_folder = _run_folder()
    assert _records(run_folder) == []
    attempts = (run_folder / "attempts.log.jsonl").read_text(encoding="utf-8")
    assert len(attempts.splitlines()) == 3
    assert "Quota/rate limit reached after 0 items; run again later" in (
        capsys.readouterr().out
    )

    client.mode = "valid"
    assert _invoke(client) == 0
    records = _records(run_folder)
    assert len(records) == 10
    assert records[0]["attempts"] == 4
    assert records[0]["item_id"] == runner._select_items(
        json.loads(runner.EVAL_PATH.read_text(encoding="utf-8")),
        "quiz",
        "dev",
    )[0]["item_id"]


def test_malformed_response_is_final_and_not_recalled(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch)
    client = MockClient(mode="malformed")

    assert _invoke(client, batch_size=1) == 0
    assert _invoke(client, batch_size=1) == 0

    records = _records(_run_folder())
    assert len(records) == 2
    assert records[0]["response_text"] == "not valid JSON"
    assert records[0]["item_id"] != records[1]["item_id"]
    assert len(client.captured_requests) == 2


def test_resume_rejects_manifest_mismatch_and_new_run_preserves_prior_data(
    tmp_path, monkeypatch
):
    _configure(tmp_path, monkeypatch)
    client = MockClient()
    assert _invoke(client, batch_size=1) == 0
    original_folder = _run_folder()
    monkeypatch.setenv("GROQ_TEMPERATURE", "0.25")

    with pytest.raises(RuntimeError, match="use --new-run or change nothing"):
        _invoke(client, batch_size=1)

    assert _invoke(client, batch_size=1, new_run=True) == 0
    assert original_folder.exists()
    assert len(list(runner.RUNS_DIR.iterdir())) == 2


def test_gold_data_never_reaches_client_and_api_key_is_not_written(
    tmp_path, monkeypatch
):
    _configure(tmp_path, monkeypatch)
    items = json.loads(runner.EVAL_PATH.read_text(encoding="utf-8"))
    client = MockClient()

    assert _invoke(client, batch_size=1) == 0
    expected_item = runner._select_items(items, "quiz", "dev")[0]
    assert client.captured_requests[0]["decision_id"] == expected_item["item_id"]

    def assert_no_gold(value):
        if isinstance(value, dict):
            for key, nested in value.items():
                assert "gold" not in key.casefold()
                assert_no_gold(nested)
        elif isinstance(value, list):
            for nested in value:
                assert_no_gold(nested)

    assert_no_gold(client.captured_requests)
    secret = b"secret-test-key-must-not-be-written"
    for path in runner.RUNS_DIR.rglob("*"):
        if path.is_file():
            assert secret not in path.read_bytes()


def test_rate_limit_uses_retry_after_and_typed_sdk_exception(
    tmp_path, monkeypatch
):
    _configure(tmp_path, monkeypatch)
    delays = []
    assert _invoke(
        MockClient(mode="rate_limit"), batch_size=1, sleep=delays.append
    ) == 3
    assert delays == [1.0, 2.0]


def test_dry_run_and_status_do_not_call_client(tmp_path, monkeypatch, capsys):
    _configure(tmp_path, monkeypatch)
    client = MockClient()

    assert _invoke(client, dry_run=True) == 0
    assert not list(runner.RUNS_DIR.iterdir())
    assert client.captured_requests == []
    assert "next items (10)" in capsys.readouterr().out

    assert _invoke(client, batch_size=1) == 0
    calls_before_status = len(client.captured_requests)
    assert _invoke(client, status=True) == 0
    assert len(client.captured_requests) == calls_before_status
    assert "1/75 final" in capsys.readouterr().out


def test_pipeline_preserves_verbatim_malformed_content():
    from decision_mirror.extraction.llm_client import Completion
    from decision_mirror.extraction.pipeline import run_item

    item = {
        "item_id": "TEST_1",
        "payload": {
            "decision_id": "TEST_1",
            "user_id": "PRIVATE_USER",
            "source_type": "decision_log",
            "decision_text": "The decision text.",
            "ontology_version": "v1.0",
            "language": "en",
        },
        "gold": {"gold_value": 0.9},
    }
    record = run_item(item, MockClient(mode="malformed"), "test prompt")

    assert record["response_text"] == "not valid JSON"
    assert record["reasoning_text"] is None


def test_pipeline_keeps_reasoning_separate_from_verbatim_content():
    from decision_mirror.extraction.llm_client import Completion
    from decision_mirror.extraction.pipeline import run_item

    class ReasoningClient:
        def complete(self, prompt, request):
            return Completion(
                content='{"result":"final"}',
                finish_reason="stop",
                usage=None,
                reasoning_text="separate reasoning",
            )

    item = {
        "item_id": "TEST_2",
        "payload": {
            "decision_id": "TEST_2",
            "user_id": "TEST_USER",
            "source_type": "decision_log",
            "decision_text": "Decision text.",
            "ontology_version": "v1.0",
            "language": "en",
        },
    }
    record = run_item(item, ReasoningClient(), "prompt")

    assert record["response_text"] == '{"result":"final"}'
    assert record["reasoning_text"] == "separate reasoning"


def test_server_error_mode_is_typed_api_failure():
    from groq import InternalServerError

    with pytest.raises(InternalServerError):
        MockClient(mode="server_error").complete("prompt", {})


def test_groq_client_fails_loudly_when_sdk_parameters_are_missing(
    monkeypatch,
):
    from decision_mirror.extraction import llm_client

    class FakeCompletions:
        def create(self, *, temperature):
            del temperature

    class FakeClient:
        chat = type("FakeChat", (), {"completions": FakeCompletions()})()

    monkeypatch.setenv("GROQ_API_KEY", "not-used")
    monkeypatch.setattr(llm_client, "Groq", lambda api_key: FakeClient())

    with pytest.raises(RuntimeError, match="max_completion_tokens"):
        llm_client.GroqClient(model="example-model")
