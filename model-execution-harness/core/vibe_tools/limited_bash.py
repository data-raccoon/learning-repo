"""Vibe tool that executes only controller-declared exact argv vectors."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
import json
import os
from pathlib import Path
import subprocess

from pydantic import BaseModel, Field

from vibe.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    InvokeContext,
    ToolError,
    ToolPermission,
)


class LimitedBashArgs(BaseModel):
    argv: list[str] = Field(
        description="Exact argument vector from the task's allowed command list."
    )


class LimitedBashResult(BaseModel):
    argv: list[str]
    stdout: str
    stderr: str
    returncode: int


class LimitedBashConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS


class LimitedBash(
    BaseTool[
        LimitedBashArgs,
        LimitedBashResult,
        LimitedBashConfig,
        BaseToolState,
    ]
):
    """Run one exact controller-admitted command without invoking a shell."""

    @classmethod
    def get_name(cls) -> str:
        return "limited_bash"

    async def run(
        self, args: LimitedBashArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[LimitedBashResult, None]:
        del ctx
        try:
            admitted = json.loads(
                os.environ.get("SMALL_CONTEXT_ALLOWED_COMMANDS", "[]")
            )
        except json.JSONDecodeError as exc:
            raise ToolError("command policy is invalid") from exc
        if (
            type(admitted) is not list
            or any(
                type(item) is not list
                or any(type(value) is not str for value in item)
                for item in admitted
            )
        ):
            raise ToolError("command policy is invalid")
        if args.argv not in admitted:
            raise ToolError("command is not admitted by the task")
        target = Path(os.environ["SMALL_CONTEXT_TARGET"]).resolve()
        timeout = int(os.environ.get("SMALL_CONTEXT_COMMAND_TIMEOUT", "120"))

        def execute() -> subprocess.CompletedProcess[str]:
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            return subprocess.run(
                args.argv,
                cwd=target,
                env=environment,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )

        try:
            completed = await asyncio.to_thread(execute)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ToolError(f"admitted command failed to execute: {exc}") from exc
        stdout = completed.stdout[-16_000:]
        stderr = completed.stderr[-16_000:]
        if completed.returncode:
            raise ToolError(
                f"command exited {completed.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        yield LimitedBashResult(
            argv=args.argv,
            stdout=stdout,
            stderr=stderr,
            returncode=completed.returncode,
        )
