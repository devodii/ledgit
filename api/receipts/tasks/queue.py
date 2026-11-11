import sys
from datetime import UTC, datetime

from pydantic import BaseModel

from receipts.connectors.errors import HumanActionRequired
from receipts.db.connection import connect
from receipts.settings import get_settings


class TaskRow(BaseModel):
    id: int
    kind: str
    description: str
    url: str
    resume_hint: str
    state: str


def notify(task_id: int, error: HumanActionRequired) -> None:
    block = (
        "\n========== NEEDS YOU ==========\n"
        f"task #{task_id}: {error.kind}\n{error.description}\n"
        f"url: {error.url}\nresume: {error.resume_hint}\n"
        "===============================\n\a"
    )
    sys.stderr.write(block)
    sys.stderr.flush()


def create_task(error: HumanActionRequired) -> int:
    settings = get_settings()
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO human_tasks (kind, description, url, resume_hint) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (error.kind, error.description, error.url, error.resume_hint),
        ).fetchone()
        conn.commit()
    assert row is not None
    task_id = int(row["id"])
    settings.tasks_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    with (settings.tasks_dir / "open.log").open("a") as log:
        log.write(f"{stamp} #{task_id} {error.kind}: {error.description} {error.url}\n")
    notify(task_id, error)
    return task_id


def list_tasks(state: str = "open") -> list[TaskRow]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, kind, description, url, resume_hint, state::text AS state "
            "FROM human_tasks WHERE state = %s::task_state ORDER BY id",
            (state,),
        ).fetchall()
    return [TaskRow.model_validate(r) for r in rows]


def resolve_task(task_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute(
            "UPDATE human_tasks SET state = 'resolved', resolved_at = now() "
            "WHERE id = %s AND state = 'open'",
            (task_id,),
        )
        conn.commit()
    return cur.rowcount > 0
