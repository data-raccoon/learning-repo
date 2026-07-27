from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from starlette.requests import Request
from starlette.responses import JSONResponse

from .service import Settings, VoxCPM2Service

PROJECT_DIR = Path(__file__).resolve().parents[2]


def create_server(
    settings: Settings | None = None, service: VoxCPM2Service | None = None
) -> FastMCP:
    selected_settings = settings or Settings.from_env(PROJECT_DIR)
    selected_service = service or VoxCPM2Service(selected_settings)
    server = FastMCP(
        "voxcpm2",
        instructions=(
            "Generate synthetic speech only with the configured, consented voice "
            "sample. The tool writes a WAV file and returns its local path."
        ),
        host="127.0.0.1",
        port=8765,
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
    )

    @server.tool(
        name="synthesize_speech",
        description=(
            "Generate a 48 kHz WAV using the configured consented VoxCPM2 "
            "reference voice. This writes a file on the local machine."
        ),
        structured_output=True,
    )
    async def synthesize_speech(
        text: str,
        filename: str | None = None,
        style: str | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        try:
            return await selected_service.synthesize(text, filename, style, seed)
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
            raise ToolError(str(error)) from error

    @server.custom_route("/health", methods=["GET"], include_in_schema=False)
    async def health(_: Request) -> JSONResponse:
        return JSONResponse(selected_service.health())

    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the localhost VoxCPM2 MCP server.")
    parser.add_argument(
        "--transport",
        choices=("streamable-http", "stdio"),
        default="streamable-http",
    )
    args = parser.parse_args()
    create_server().run(transport=args.transport)


if __name__ == "__main__":
    main()
