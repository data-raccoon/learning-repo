from __future__ import annotations

import asyncio
import os
import re
import secrets
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

MAX_TEXT_CHARS = 4_000
MAX_STYLE_CHARS = 200
DEFAULT_MODEL = "openbmb/VoxCPM2"
DEFAULT_SAMPLE_RATE = 48_000
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    reference_path: Path
    transcript_path: Path
    output_dir: Path
    model_id: str = DEFAULT_MODEL
    device: str = "cuda:0"
    local_files_only: bool = True
    optimize: bool = False
    dtype: str = "auto"
    inference_timesteps: int = 10
    retry_badcase: bool = True
    backend: str = "cpp"
    cpp_binary: Path = Path()
    base_model_path: Path = Path()
    acoustic_model_path: Path = Path()
    max_steps: int = 200
    process_timeout_seconds: int = 600

    @classmethod
    def from_env(cls, project_dir: Path) -> "Settings":
        data_dir = Path(
            os.environ.get("VOXCPM2_DATA_DIR", project_dir / "data")
        ).expanduser().resolve()
        home = Path.home()
        return cls(
            data_dir=data_dir,
            reference_path=Path(
                os.environ.get(
                    "VOXCPM2_REFERENCE_WAV",
                    data_dir / "reference-sample.wav",
                )
            ).expanduser().resolve(),
            transcript_path=Path(
                os.environ.get("VOXCPM2_REFERENCE_TEXT", data_dir / "reference.txt")
            ).expanduser().resolve(),
            output_dir=Path(
                os.environ.get("VOXCPM2_OUTPUT_DIR", data_dir / "outputs")
            ).expanduser().resolve(),
            model_id=os.environ.get("VOXCPM2_MODEL", DEFAULT_MODEL),
            device=os.environ.get("VOXCPM2_DEVICE", "cuda:0"),
            local_files_only=_env_bool("VOXCPM2_LOCAL_FILES_ONLY", True),
            optimize=_env_bool("VOXCPM2_OPTIMIZE", False),
            dtype=os.environ.get("VOXCPM2_DTYPE", "auto").strip().lower(),
            inference_timesteps=_env_int(
                "VOXCPM2_INFERENCE_TIMESTEPS", default=10, minimum=1, maximum=50
            ),
            retry_badcase=_env_bool("VOXCPM2_RETRY_BADCASE", True),
            backend=os.environ.get("VOXCPM2_BACKEND", "cpp").strip().lower(),
            cpp_binary=Path(
                os.environ.get(
                    "VOXCPM2_CPP_BINARY",
                    home
                    / "git"
                    / "llama.cpp-omni"
                    / "build-vulkan"
                    / "bin"
                    / "Release"
                    / "voxcpm2-cli.exe",
                )
            ).expanduser().resolve(),
            base_model_path=Path(
                os.environ.get(
                    "VOXCPM2_BASE_MODEL",
                    home
                    / ".cache"
                    / "voxcpm2-gguf"
                    / "VoxCPM2-BaseLM-Q8_0.gguf",
                )
            ).expanduser().resolve(),
            acoustic_model_path=Path(
                os.environ.get(
                    "VOXCPM2_ACOUSTIC_MODEL",
                    home
                    / ".cache"
                    / "voxcpm2-gguf"
                    / "VoxCPM2-Acoustic-F16.gguf",
                )
            ).expanduser().resolve(),
            max_steps=_env_int(
                "VOXCPM2_MAX_STEPS", default=200, minimum=1, maximum=500
            ),
            process_timeout_seconds=_env_int(
                "VOXCPM2_PROCESS_TIMEOUT_SECONDS",
                default=600,
                minimum=30,
                maximum=3600,
            ),
        )


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return parsed


def select_runtime_dtype(
    requested: str, device: str, cuda_capability: tuple[int, int] | None
) -> str:
    aliases = {
        "auto": "auto",
        "bfloat16": "bfloat16",
        "bf16": "bfloat16",
        "float16": "float16",
        "fp16": "float16",
        "float32": "float32",
        "fp32": "float32",
    }
    selected = aliases.get(requested)
    if selected is None:
        raise ValueError("VOXCPM2_DTYPE must be auto, bfloat16, float16, or float32")
    if selected != "auto":
        return selected
    if device.startswith("cuda") and cuda_capability is not None:
        return "bfloat16" if cuda_capability[0] >= 8 else "float16"
    return "float32"


def validate_text(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    normalized = " ".join(text.split())
    if not normalized:
        raise ValueError("text must not be empty")
    if len(normalized) > MAX_TEXT_CHARS:
        raise ValueError(f"text must not exceed {MAX_TEXT_CHARS} characters")
    return normalized


def validate_style(style: str | None) -> str | None:
    if style is None:
        return None
    normalized = " ".join(style.split())
    if not normalized:
        return None
    if len(normalized) > MAX_STYLE_CHARS:
        raise ValueError(f"style must not exceed {MAX_STYLE_CHARS} characters")
    if any(character in normalized for character in "()\r\n"):
        raise ValueError("style must not contain parentheses or line breaks")
    return normalized


def safe_output_name(filename: str | None, seed: int) -> str:
    requested = filename.strip() if filename else f"speech-{seed}"
    if Path(requested).name != requested or requested in {".", ".."}:
        raise ValueError("filename must be a basename without directories")
    if requested.lower().endswith(".wav"):
        requested = requested[:-4]
    sanitized = _SAFE_FILENAME.sub("-", requested).strip(" .-_")
    if not sanitized:
        raise ValueError("filename must contain a letter or number")
    return f"{sanitized[:96]}.wav"


class VoxCPM2Service:
    def __init__(
        self,
        settings: Settings,
        model_factory: Callable[[Settings], Any] | None = None,
        audio_writer: Callable[[Path, Any, int], None] | None = None,
        command_runner: Callable[..., Any] | None = None,
    ) -> None:
        self.settings = settings
        self._model_factory = model_factory
        self._audio_writer = audio_writer or self._write_audio
        self._command_runner = command_runner or subprocess.run
        self._model: Any | None = None
        self._model_guard = threading.Lock()
        self._job_lock = asyncio.Lock()

    def health(self) -> dict[str, Any]:
        runtime_available = (
            self.settings.cpp_binary.is_file()
            and self.settings.base_model_path.is_file()
            and self.settings.acoustic_model_path.is_file()
        )
        ready = (
            runtime_available
            if self.settings.backend == "cpp"
            else self._model is not None
        )
        return {
            "status": "ready" if ready else "not_ready",
            "backend": self.settings.backend,
            "model": self.settings.model_id,
            "device": self.settings.device,
            "dtype": self.settings.dtype,
            "reference_available": self.settings.reference_path.is_file(),
            "transcript_available": self._read_transcript() is not None,
            "busy": self._job_lock.locked(),
        }

    async def synthesize(
        self,
        text: str,
        filename: str | None = None,
        style: str | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        normalized_text = validate_text(text)
        normalized_style = validate_style(style)
        selected_seed = seed if seed is not None else secrets.randbelow(2**31)
        if not isinstance(selected_seed, int) or isinstance(selected_seed, bool):
            raise ValueError("seed must be an integer")
        if selected_seed < 0 or selected_seed >= 2**31:
            raise ValueError("seed must be between 0 and 2147483647")
        output_name = safe_output_name(filename, selected_seed)

        if not self.settings.reference_path.is_file():
            raise FileNotFoundError(
                "Configured reference audio is missing; add "
                "data/reference-sample.wav or set VOXCPM2_REFERENCE_WAV"
            )

        async with self._job_lock:
            return await asyncio.to_thread(
                self._synthesize_sync,
                normalized_text,
                output_name,
                normalized_style,
                selected_seed,
            )

    def _synthesize_sync(
        self, text: str, output_name: str, style: str | None, seed: int
    ) -> dict[str, Any]:
        if self._model_factory is None and self.settings.backend == "cpp":
            return self._synthesize_cpp(text, output_name, style, seed)

        model = self._get_model()
        transcript = self._read_transcript()
        generation_text = f"({style}){text}" if style else text
        kwargs: dict[str, Any] = {
            "text": generation_text,
            "reference_wav_path": str(self.settings.reference_path),
            "cfg_value": 2.0,
            "inference_timesteps": self.settings.inference_timesteps,
            "normalize": True,
            "denoise": False,
            "retry_badcase": self.settings.retry_badcase,
            "retry_badcase_max_times": 2,
            "seed": seed,
        }
        clone_mode = "isolated_reference"
        if transcript is not None:
            kwargs["prompt_wav_path"] = str(self.settings.reference_path)
            kwargs["prompt_text"] = transcript
            clone_mode = "transcript_assisted"

        waveform = model.generate(**kwargs)
        sample_rate = int(
            getattr(getattr(model, "tts_model", None), "sample_rate", DEFAULT_SAMPLE_RATE)
        )
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (self.settings.output_dir / output_name).resolve()
        if output_path.parent != self.settings.output_dir.resolve():
            raise ValueError("output path escaped the configured output directory")
        self._audio_writer(output_path, waveform, sample_rate)
        duration = len(waveform) / sample_rate
        return {
            "path": str(output_path),
            "sample_rate": sample_rate,
            "duration_seconds": round(duration, 3),
            "seed": seed,
            "clone_mode": clone_mode,
            "backend": "python",
        }

    def _synthesize_cpp(
        self, text: str, output_name: str, style: str | None, seed: int
    ) -> dict[str, Any]:
        required = (
            self.settings.cpp_binary,
            self.settings.base_model_path,
            self.settings.acoustic_model_path,
        )
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise FileNotFoundError(
                "Quantized VoxCPM2 runtime is incomplete: " + ", ".join(missing)
            )

        generation_text = f"({style}){text}" if style else text
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (self.settings.output_dir / output_name).resolve()
        if output_path.parent != self.settings.output_dir.resolve():
            raise ValueError("output path escaped the configured output directory")

        transcript = self._read_transcript()
        command = [
            str(self.settings.cpp_binary),
            "-t",
            generation_text,
            "-o",
            str(output_path),
            "--timesteps",
            str(self.settings.inference_timesteps),
            "--steps",
            str(self.settings.max_steps),
            "--seed",
            str(seed),
        ]
        clone_mode = "isolated_reference"
        if transcript is None:
            command.extend(["-r", str(self.settings.reference_path)])
        else:
            command.extend(
                [
                    "--prompt-wav",
                    str(self.settings.reference_path),
                    "--prompt-text",
                    transcript,
                ]
            )
            clone_mode = "transcript_assisted"
        command.extend(
            [
                str(self.settings.base_model_path),
                str(self.settings.acoustic_model_path),
            ]
        )

        try:
            completed = self._command_runner(
                command,
                cwd=self.settings.cpp_binary.parent,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.settings.process_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "Quantized VoxCPM2 inference exceeded "
                f"{self.settings.process_timeout_seconds} seconds"
            ) from error
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise RuntimeError(
                f"Quantized VoxCPM2 failed with exit code {completed.returncode}: "
                f"{detail[-2_000:]}"
            )
        if not output_path.is_file():
            raise RuntimeError("Quantized VoxCPM2 exited without writing a WAV file")

        import soundfile as sf

        info = sf.info(str(output_path))
        return {
            "path": str(output_path),
            "sample_rate": info.samplerate,
            "duration_seconds": round(info.duration, 3),
            "seed": seed,
            "clone_mode": clone_mode,
            "backend": "cpp-vulkan-q8",
        }

    def _get_model(self) -> Any:
        if self._model_factory is None:
            self._model_factory = self._load_model
        if self._model is None:
            with self._model_guard:
                if self._model is None:
                    self._model = self._model_factory(self.settings)
        return self._model

    def _read_transcript(self) -> str | None:
        if not self.settings.transcript_path.is_file():
            return None
        transcript = " ".join(
            self.settings.transcript_path.read_text(encoding="utf-8").split()
        )
        return transcript or None

    @staticmethod
    def _load_model(settings: Settings) -> Any:
        import torch
        from voxcpm import VoxCPM
        from voxcpm.model import voxcpm2
        from unittest.mock import patch

        capability = (
            torch.cuda.get_device_capability(settings.device)
            if settings.device.startswith("cuda") and torch.cuda.is_available()
            else None
        )
        runtime_dtype = select_runtime_dtype(
            settings.dtype, settings.device, capability
        )

        with patch.object(
            voxcpm2, "pick_runtime_dtype", return_value=runtime_dtype
        ):
            return VoxCPM.from_pretrained(
                settings.model_id,
                load_denoiser=False,
                local_files_only=settings.local_files_only,
                optimize=settings.optimize,
                device=settings.device,
            )

    @staticmethod
    def _write_audio(path: Path, waveform: Any, sample_rate: int) -> None:
        import soundfile as sf

        sf.write(str(path), waveform, sample_rate)
