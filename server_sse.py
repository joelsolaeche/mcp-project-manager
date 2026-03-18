"""SSE transport entrypoint for remote deployment.

Instead of communicating via stdin/stdout (stdio), this wraps the same MCP server
in an HTTP web app using Starlette + uvicorn. Clients connect via:
  - GET /sse — opens an SSE stream (long-lived connection)
  - POST /messages/ — sends messages to the server

This is the entrypoint you deploy to Railway/Render.
"""

import asyncio
import os
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp.server.sse import SseServerTransport
from mcp.server import InitializationOptions, NotificationOptions

from server import server
from db import init_db

# SSE transport — handles the HTTP <-> MCP protocol translation
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    """Handle incoming SSE connections from MCP clients."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        init_options = InitializationOptions(
            server_name="project-manager",
            server_version="0.1.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )
        await server.run(
            streams[0], streams[1], init_options
        )


async def handle_messages(request: Request):
    """Handle incoming messages from MCP clients."""
    await sse.handle_post_message(request.scope, request.receive, request._send)


async def health(request: Request):
    """Health check endpoint for deployment platforms."""
    return JSONResponse({"status": "ok", "server": "project-manager"})


# Initialize DB on startup
async def on_startup():
    await init_db()


app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        Route("/sse", handle_sse, methods=["GET"]),
        Route("/messages/", handle_messages, methods=["POST"]),
    ],
    on_startup=[on_startup],
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
