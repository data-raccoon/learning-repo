import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator.adapters import LocalChatAdapter
from agent_orchestrator.contracts import Job, Limits, Model, ModelProfile


class FakeResponse:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.value).encode("utf-8")


class LocalChatAdapterTests(unittest.TestCase):
    def job(self, output_tokens=120) -> Job:
        return Job(
            1, "turn", "Return one turn", "target", "read", "low", "low", "inference",
            limits=Limits(max_tokens=32_000, max_output_tokens=output_tokens),
        )

    @staticmethod
    def model() -> Model:
        return Model("local", "local-ministral", "ministral-3b-q4", .5, 32_768, 0, 0, "2026-01-01", ("text",), ())

    @staticmethod
    def profile() -> ModelProfile:
        return ModelProfile("local", "local", "chat", "eligible", .9, (), "inference")

    def test_output_budget_is_separate_from_full_token_budget(self):
        response = FakeResponse({
            "model": "ministral-3b-q4", "choices": [{"message": {"content": "done"}}], "usage": {},
        })
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key = root / "key.txt"
            key.write_text("secret", encoding="ascii")
            with patch("agent_orchestrator.adapters.urllib.request.urlopen", return_value=response) as urlopen:
                result = LocalChatAdapter(key_file=key).run(self.job(), root, self.model(), self.profile())
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["max_tokens"], 120)
        self.assertTrue(result.ok)
        self.assertTrue(result.attestation["matched"])

    def test_missing_or_different_effective_model_fails_closed(self):
        for reported in (None, "some-cloud-model"):
            response = FakeResponse({
                "model": reported, "choices": [{"message": {"content": "done"}}], "usage": {},
            })
            with self.subTest(reported=reported), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                key = root / "key.txt"
                key.write_text("secret", encoding="ascii")
                with patch("agent_orchestrator.adapters.urllib.request.urlopen", return_value=response):
                    result = LocalChatAdapter(key_file=key).run(self.job(), root, self.model(), self.profile())
                self.assertFalse(result.ok)
                self.assertFalse(result.attestation["matched"])


if __name__ == "__main__":
    unittest.main()
