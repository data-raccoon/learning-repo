"""Run one Vibe prompt with native image attachments and emit Vibe JSON output.

Vibe's interactive UI turns @mentioned images into ``LLMMessage.images``. Its
programmatic CLI currently passes the prompt straight to ``AgentLoop.act`` and
therefore loses that attachment plumbing. This small adapter uses the same Vibe
agent loop, configuration, authentication, tools, limits, and JSON formatter,
while supplying image files through the native ``images=`` argument.
"""

from __future__ import annotations

import argparse
import asyncio
from contextlib import aclosing
import mimetypes
from pathlib import Path

from vibe import __version__
from vibe.core.agent_loop import AgentLoop
from vibe.core.config import VibeConfig, load_dotenv_values
from vibe.core.config.harness_files import init_harness_files_manager
from vibe.core.config.orchestrator_legacy import LegacyConfigOrchestrator
from vibe.core.output_formatters import create_formatter
from vibe.core.telemetry.build_metadata import build_launch_context
from vibe.core.telemetry.types import ClientMetadata
from vibe.core.types import FileImageSource, ImageAttachment, OutputFormat


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--image", type=Path, action="append", default=[])
    parser.add_argument("--enabled-tool", action="append", default=[])
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--max-price", type=float, default=2.0)
    parser.add_argument("--max-tokens", type=int, default=50_000)
    return parser.parse_args()


def image_attachment(path: Path) -> ImageAttachment:
    resolved = path.resolve(strict=True)
    mime_type, _ = mimetypes.guess_type(resolved.name)
    if mime_type not in {"image/png", "image/jpeg", "image/gif", "image/webp"}:
        raise ValueError(f"Unsupported image type: {resolved}")
    if resolved.stat().st_size > 10 * 1024 * 1024:
        raise ValueError(f"Image exceeds Vibe's 10 MiB limit: {resolved}")
    return ImageAttachment(
        source=FileImageSource(path=resolved),
        alias=resolved.name,
        mime_type=mime_type,
    )


def main() -> None:
    args = parse_args()
    init_harness_files_manager("user", "project")
    load_dotenv_values()
    config = VibeConfig.load()
    config.enabled_tools = args.enabled_tool
    config.disabled_tools = [
        *config.disabled_tools,
        "ask_user_question",
        "exit_plan_mode",
    ]
    config.bypass_tool_permissions = True

    prompt = args.prompt_file.resolve(strict=True).read_text(encoding="utf-8")
    images = [image_attachment(path) for path in args.image]
    formatter = create_formatter(OutputFormat.JSON)
    client = ClientMetadata(name="glimweave_multimodal_runner", version="1")
    agent_loop = AgentLoop(
        LegacyConfigOrchestrator(config),
        agent_name="default",
        message_observer=formatter.on_message_added,
        max_turns=args.max_turns,
        max_price=args.max_price,
        max_session_tokens=args.max_tokens,
        enable_streaming=False,
        headless=True,
        launch_context=build_launch_context(
            agent_entrypoint="programmatic",
            agent_version=__version__,
            client_name=client.name,
            client_version=client.version,
        ),
    )

    async def run() -> None:
        try:
            await agent_loop.initialize_experiments()
            agent_loop.emit_new_session_telemetry()
            async with aclosing(agent_loop.act(prompt, images=images or None)) as events:
                async for event in events:
                    formatter.on_event(event)
            formatter.finalize()
        finally:
            agent_loop.emit_session_closed_telemetry()
            await agent_loop.aclose()
            await agent_loop.telemetry_client.aclose()

    asyncio.run(run())


if __name__ == "__main__":
    main()
