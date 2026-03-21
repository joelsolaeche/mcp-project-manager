# MCP Project Manager

A task management MCP (Model Context Protocol) server that plugs directly into Claude Code. Create, list, and update tasks through natural language — Claude calls the tools automatically.

Built with Python, FastMCP, and SQLite. Deployable to any platform that supports Python (currently live on Render).

## Live Deployment

| | |
|---|---|
| Base URL | https://mcp-project-manager-00dp.onrender.com |
| Health check | https://mcp-project-manager-00dp.onrender.com/health |
| SSE endpoint | https://mcp-project-manager-00dp.onrender.com/sse |

## Tools

| Tool | Description | Required params |
|---|---|---|
| `create_task` | Create a new task | `title`, `priority` |
| `list_tasks` | List tasks, with optional filters | — |
| `update_task` | Update a task's status by ID | `id`, `status` |

**Priority levels:** `low` · `medium` · `high` · `critical`

**Status values:** `todo` · `in_progress` · `done`

## Project Structure

```
server.py       # MCP server — tool definitions and request routing (stdio transport)
server_sse.py   # HTTP wrapper for remote deployment (SSE transport via Starlette + uvicorn)
db.py           # Async SQLite database layer (aiosqlite)
tasks.db        # SQLite database — auto-created on first run
Procfile        # Render/Railway deploy command
pyproject.toml  # Dependencies and project metadata
```

## Data Model

Each task has:

```
id          INTEGER  Auto-incremented primary key
title       TEXT     Short description of the task
description TEXT     Optional longer details
priority    TEXT     low | medium | high | critical
status      TEXT     todo | in_progress | done  (default: todo)
created_at  TEXT     UTC ISO 8601 timestamp
updated_at  TEXT     UTC ISO 8601 timestamp
```

## Running Locally

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
# Install dependencies
uv sync

# Run in stdio mode (for Claude Code local integration)
uv run python server.py

# Run in SSE mode (HTTP server for remote/testing)
uv run python server_sse.py
```

The SSE server listens on port `8000` by default. Set the `PORT` environment variable to override.

## Connecting to Claude Code

The `.mcp.json` file at the root of this repo configures the local MCP server for Claude Code automatically:

```json
{
  "mcpServers": {
    "project-manager": {
      "command": "uv",
      "args": ["run", "python", "server.py"]
    }
  }
}
```

Once connected, you can talk to Claude naturally — "create a high priority task to fix the login bug" — and it will call the right tool.

## Tech Stack

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — protocol implementation
- [aiosqlite](https://github.com/omnilib/aiosqlite) — async SQLite
- [Starlette](https://www.starlette.io/) + [uvicorn](https://www.uvicorn.org/) — HTTP server for SSE transport
- [uv](https://docs.astral.sh/uv/) — dependency management
