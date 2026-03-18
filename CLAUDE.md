# MCP Project Manager

## What this is
An MCP (Model Context Protocol) server that provides task management tools to Claude Code. Built with Python, FastMCP, and SQLite.

## Architecture
- `server.py` — MCP server with 3 tools: create_task, list_tasks, update_task (stdio transport)
- `server_sse.py` — SSE transport wrapper for remote deployment (Starlette + uvicorn)
- `db.py` — Async SQLite database layer using aiosqlite
- `tasks.db` — SQLite database (auto-created, do not commit)

## Running locally
```bash
uv run python server.py        # stdio mode (for Claude Code local)
uv run python server_sse.py    # SSE mode (for remote/testing)
```

## Deployed at
- Render: https://mcp-project-manager-00dp.onrender.com
- Health check: /health
- SSE endpoint: /sse

## Conventions
- Use `uv` for dependency management, not pip
- All database operations go through `db.py` — never write raw SQL in server files
- Tool descriptions must be clear and specific — they are context for the LLM
- Prefix commits with feat:, fix:, or chore:
