import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server import InitializationOptions, NotificationOptions

from db import init_db, create_task, list_tasks, update_task

# Create the MCP server instance — the name is what shows up in Claude Code
server = Server("project-manager")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Declare the tools this server exposes.

    Each tool has a name, description (used by the LLM to decide WHEN to call it),
    and an inputSchema (JSON Schema defining the parameters).
    Good descriptions are critical — they're the LLM's only guide for tool selection.
    """
    return [
        Tool(
            name="create_task",
            description="Create a new project task with a title, description, and priority level. Use this when the user wants to add a new task or work item.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short, descriptive title for the task",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of what the task involves",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level of the task",
                    },
                },
                "required": ["title", "priority"],
            },
        ),
        Tool(
            name="list_tasks",
            description="List all project tasks, optionally filtered by status and/or priority. Use this to show the current state of tasks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "done"],
                        "description": "Filter tasks by status",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Filter tasks by priority",
                    },
                },
            },
        ),
        Tool(
            name="update_task",
            description="Update the status of an existing task by its ID. Use this to mark tasks as in progress or done.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The task ID to update",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "done"],
                        "description": "The new status for the task",
                    },
                },
                "required": ["id", "status"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to the appropriate database function.

    This is the handler that runs when Claude actually invokes one of our tools.
    It receives the tool name and arguments, calls the DB layer, and returns
    the result as TextContent (JSON string that Claude can read).
    """
    if name == "create_task":
        task = await create_task(
            title=arguments["title"],
            description=arguments.get("description", ""),
            priority=arguments["priority"],
        )
        return [TextContent(type="text", text=json.dumps(task, indent=2))]

    elif name == "list_tasks":
        tasks = await list_tasks(
            status=arguments.get("status"),
            priority=arguments.get("priority"),
        )
        if not tasks:
            return [TextContent(type="text", text="No tasks found matching the filters.")]
        return [TextContent(type="text", text=json.dumps(tasks, indent=2))]

    elif name == "update_task":
        task = await update_task(
            task_id=arguments["id"],
            status=arguments["status"],
        )
        if task is None:
            return [TextContent(type="text", text=f"Error: Task with ID {arguments['id']} not found.")]
        return [TextContent(type="text", text=json.dumps(task, indent=2))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    # Initialize the database (creates table if needed)
    await init_db()

    # Start the server with stdio transport
    # stdio = communication via stdin/stdout (how Claude Code talks to local MCP servers)
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="project-manager",
            server_version="0.1.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
