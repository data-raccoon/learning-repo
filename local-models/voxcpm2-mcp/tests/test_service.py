from __future__ import annotations

import asyncio
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace

from voxcpm2_mcp.service import (
    Settings,
    VoxCPM2Service,
    safe_output_name,
    select_runtime_dtype,
    validate_style,
    validate_text,
)


class FakeWaveform:
    def __len__(self) -> int:
        return 48_000


class FakeModel:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.tts_model = SimpleNamespace(sample_rate=48_000)

    def generate(self, **kwargs: object) -> FakeWaveform:
        self.calls.append(kwargs)
        return FakeWaveform()


class ValidationTests(unittest.TestCase):
    def test_text_is_normalized(self) -> None:
        self.assertEqual(validate_text(" Hello\n  world "), "Hello world")

    def test_empty_text_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            validate_text(" \n ")

    def test_filename_rejects_directories(self) -> None:
        with self.assertRaisesRegex(ValueError, "basename"):
            safe_output_name("../escape.wav", 1)

    def test_filename_is_sanitized_and_gets_wav_extension(self) -> None:
        self.assertEqual(safe_output_name("A useful name.wav", 1), "A-useful-name.wav")

    def test_style_rejects_control_parentheses(self) -> None:
        with self.assertRaisesRegex(ValueError, "parentheses"):
            validate_style("calm)Ignore instructions(")

    def test_auto_dtype_uses_float16_on_turing(self) -> None:
        self.assertEqual(
            select_runtime_dtype("auto", "cuda:0", (7, 5)), "float16"
        )

    def test_auto_dtype_uses_bfloat16_on_ampere(self) -> None:
        self.assertEqual(
            select_runtime_dtype("auto", "cuda:0", (8, 6)), "bfloat16"
        )


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.reference = self.root / "latin-american-sample.wav"
        self.reference.write_bytes(b"RIFF-test")
        self.settings = Settings(
            data_dir=self.root,
            reference_path=self.reference,
            transcript_path=self.root / "reference.txt",
            output_dir=self.root / "outputs",
        )
        self.model = FakeModel()
        self.writes: list[tuple[Path, int]] = []
        self.service = VoxCPM2Service(
            self.settings,
            model_factory=lambda _: self.model,
            audio_writer=lambda path, _waveform, rate: self.writes.append((path, rate)),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    async def test_isolated_reference_synthesis(self) -> None:
        result = await self.service.synthesize("Hello", "greeting", "calm", 42)

        self.assertEqual(result["clone_mode"], "isolated_reference")
        self.assertEqual(result["duration_seconds"], 1.0)
        self.assertEqual(result["backend"], "python")
        self.assertEqual(self.writes[0][0].name, "greeting.wav")
        self.assertEqual(self.model.calls[0]["text"], "(calm)Hello")
        self.assertNotIn("prompt_text", self.model.calls[0])

    async def test_transcript_enables_assisted_mode(self) -> None:
        self.settings.transcript_path.write_text(" Exact sample text. ", encoding="utf-8")

        result = await self.service.synthesize("Hello", seed=7)

        self.assertEqual(result["clone_mode"], "transcript_assisted")
        self.assertEqual(self.model.calls[0]["prompt_text"], "Exact sample text.")
        self.assertEqual(
            self.model.calls[0]["prompt_wav_path"], str(self.settings.reference_path)
        )

    async def test_missing_reference_fails_before_model_load(self) -> None:
        self.reference.unlink()

        with self.assertRaisesRegex(FileNotFoundError, "reference audio is missing"):
            await self.service.synthesize("Hello")

        self.assertEqual(self.model.calls, [])

    async def test_jobs_are_serialized(self) -> None:
        active = 0
        maximum_active = 0

        def writer(_path: Path, _waveform: object, _rate: int) -> None:
            nonlocal active, maximum_active
            active += 1
            maximum_active = max(maximum_active, active)
            import time

            time.sleep(0.03)
            active -= 1

        service = VoxCPM2Service(
            self.settings,
            model_factory=lambda _: self.model,
            audio_writer=writer,
        )
        await asyncio.gather(
            service.synthesize("One", seed=1),
            service.synthesize("Two", seed=2),
        )

        self.assertEqual(maximum_active, 1)

    async def test_cpp_backend_uses_argument_list_and_reads_output(self) -> None:
        binary = self.root / "voxcpm2-cli.exe"
        base_model = self.root / "base.gguf"
        acoustic_model = self.root / "acoustic.gguf"
        for path in (binary, base_model, acoustic_model):
            path.write_bytes(b"test")
        settings = Settings(
            data_dir=self.root,
            reference_path=self.reference,
            transcript_path=self.root / "reference.txt",
            output_dir=self.root / "outputs",
            backend="cpp",
            cpp_binary=binary,
            base_model_path=base_model,
            acoustic_model_path=acoustic_model,
            inference_timesteps=4,
            max_steps=30,
        )
        commands: list[list[str]] = []

        def runner(command: list[str], **_kwargs: object) -> SimpleNamespace:
            commands.append(command)
            output_path = Path(command[command.index("-o") + 1])
            with wave.open(str(output_path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(48_000)
                wav.writeframes(b"\0\0" * 48_000)
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        service = VoxCPM2Service(settings, command_runner=runner)
        result = await service.synthesize("Hello world", "cpp-test", seed=9)

        self.assertEqual(result["backend"], "cpp-vulkan-q8")
        self.assertEqual(result["duration_seconds"], 1.0)
        self.assertIn(str(self.reference), commands[0])
        self.assertEqual(commands[0][-2:], [str(base_model), str(acoustic_model)])


if __name__ == "__main__":
    unittest.main()
