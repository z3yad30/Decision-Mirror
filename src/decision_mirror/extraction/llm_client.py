from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from inspect import signature
from typing import Any, Protocol

from dotenv import load_dotenv
from groq import Groq


@dataclass(frozen=True)
class Completion:
    content: str
    finish_reason: str | None
    usage: dict[str, Any] | None
    reasoning_text: str | None = None


class LLMClient(Protocol):
    def complete(
        self, prompt: str, request: dict[str, Any]
    ) -> Completion: ...


class GroqClient:
    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_completion_tokens: int = 4096,
        reasoning_effort: str = "medium",
        response_format: dict[str, str] | None = None,
    ) -> None:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY was not found in the environment or .env")

        self.model = model
        self.temperature = temperature
        self.max_completion_tokens = max_completion_tokens
        self.reasoning_effort = reasoning_effort
        self.response_format = response_format or {"type": "json_object"}
        self._client = Groq(api_key=api_key)
        self._verify_parameters()

    def _verify_parameters(self) -> None:
        supported = signature(
            self._client.chat.completions.create
        ).parameters
        required = {
            "temperature",
            "max_completion_tokens",
            "reasoning_effort",
            "response_format",
        }
        missing = sorted(required.difference(supported))
        if missing:
            raise RuntimeError(
                "Installed Groq SDK does not support required completion "
                f"parameter(s): {', '.join(missing)}"
            )

    def complete(
        self, prompt: str, request: dict[str, Any]
    ) -> Completion:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": json.dumps(request, ensure_ascii=False),
                },
            ],
            temperature=self.temperature,
            max_completion_tokens=self.max_completion_tokens,
            reasoning_effort=self.reasoning_effort,
            response_format=self.response_format,
        )
        choice = response.choices[0]
        message = choice.message
        usage = response.usage
        if usage is not None:
            usage = usage.model_dump(mode="json")
        content = message.content
        return Completion(
            content=content if isinstance(content, str) else "",
            finish_reason=choice.finish_reason,
            usage=usage,
            reasoning_text=getattr(message, "reasoning", None),
        )


class MockClient:
    def __init__(self, mode: str = "valid") -> None:
        if mode not in {"valid", "malformed", "rate_limit", "server_error"}:
            raise ValueError(f"unsupported mock mode: {mode}")
        self.mode = mode
        self.captured_requests: list[dict[str, Any]] = []

    def complete(
        self, prompt: str, request: dict[str, Any]
    ) -> Completion:
        del prompt
        self.captured_requests.append(request)

        if self.mode == "rate_limit":
            from groq import RateLimitError
            from httpx import Request, Response

            response = Response(
                429,
                headers={"retry-after": "0"},
                request=Request("POST", "https://api.groq.com"),
            )
            raise RateLimitError(
                "simulated rate limit",
                response=response,
                body={"error": {"message": "simulated rate limit"}},
            )
        if self.mode == "server_error":
            from groq import InternalServerError
            from httpx import Request, Response

            response = Response(
                500, request=Request("POST", "https://api.groq.com")
            )
            raise InternalServerError(
                "simulated server error",
                response=response,
                body={"error": {"message": "simulated server error"}},
            )
        if self.mode == "malformed":
            return Completion(
                content="not valid JSON",
                finish_reason="stop",
                usage={"total_tokens": 0},
            )

        traits = []
        for index in range(1, 7):
            trait_id = f"T{index:02d}"
            if index == 1:
                traits.append(
                    {
                        "trait_id": trait_id,
                        "trait_name": "Risk Tolerance",
                        "score": 0.5,
                        "confidence": 0.5,
                        "evidence": [request["decision_text"]],
                        "situational_factor": None,
                        "context_notes": "The decision text supports a score.",
                    }
                )
            else:
                names = {
                    2: "Time Horizon",
                    3: "Locus of Priority",
                    4: "Decisiveness Speed",
                    5: "Emotional vs. Analytical Weighting",
                    6: "Self-Consistency",
                }
                traits.append(
                    {
                        "trait_id": trait_id,
                        "trait_name": names[index],
                        "score": None,
                        "confidence": 0.0,
                        "evidence": [],
                        "situational_factor": None,
                        "context_notes": "Insufficient evidence in this item.",
                    }
                )
        content = json.dumps(
            {
                "decision_id": request["decision_id"],
                "extraction_status": "success",
                "traits": traits,
            },
            ensure_ascii=False,
        )
        return Completion(
            content=content,
            finish_reason="stop",
            usage={"total_tokens": 0},
        )
