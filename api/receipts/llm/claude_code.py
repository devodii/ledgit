import json
import subprocess

from receipts.llm.base import LLMError, LLMProvider


class ClaudeCodeProvider(LLMProvider):
    name = "claude_code"

    def __init__(self, model: str = "", timeout: int = 600) -> None:
        self.model = model or "claude-code-default"
        self._model_arg = model
        self.timeout = timeout

    def complete(self, system: str, prompt: str) -> str:
        cmd = [
            "claude",
            "-p",
            "--output-format",
            "json",
            "--tools",
            "",
            "--no-session-persistence",
            "--disable-slash-commands",
            "--append-system-prompt",
            system,
        ]
        if self._model_arg:
            cmd += ["--model", self._model_arg]
        try:
            run = subprocess.run(
                cmd, input=prompt, capture_output=True, text=True, timeout=self.timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise LLMError("claude -p timed out") from exc
        if run.returncode != 0:
            raise LLMError(f"claude -p failed: {run.stderr[-300:] or run.stdout[-300:]}")
        try:
            payload = json.loads(run.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"claude -p returned non JSON: {run.stdout[:200]}") from exc
        if payload.get("is_error"):
            raise LLMError(f"claude -p error: {payload.get('result', '')[:300]}")
        usage = payload.get("modelUsage") or {}
        if usage:
            self.model = sorted(usage)[0]
        result = payload.get("result", "")
        return str(result)
