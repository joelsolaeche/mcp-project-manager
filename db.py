import aiosqlite
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "tasks.db"


async def init_db():
    """Create the tasks table if it doesn't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'critical')),
                status TEXT NOT NULL DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def create_task(title: str, description: str, priority: str) -> dict:
    """Insert a new task and return it as a dict."""
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "INSERT INTO tasks (title, description, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (title, description, priority, now, now),
        )
        await db.commit()
        row = await (await db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,))).fetchone()
        return dict(row)


async def list_tasks(status: str | None = None, priority: str | None = None) -> list[dict]:
    """Query tasks with optional filters. Returns list ordered by id DESC."""
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list[str] = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY id DESC"

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(query, params)).fetchall()
        return [dict(row) for row in rows]


async def update_task(task_id: int, status: str) -> dict | None:
    """Update a task's status. Returns updated task or None if not found."""
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, task_id),
        )
        await db.commit()
        if cursor.rowcount == 0:
            return None
        row = await (await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))).fetchone()
        return dict(row)
