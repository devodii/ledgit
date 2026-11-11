from typing import Annotated

from fastapi import APIRouter, Depends

from receipts.db.connection import Conn, get_conn
from receipts.models.api import HumanTask, TaskList

router = APIRouter(tags=["admin"])


@router.get("/admin/tasks", operation_id="listAdminTasks")
def admin_tasks(conn: Annotated[Conn, Depends(get_conn)]) -> TaskList:
    rows = conn.execute(
        "SELECT id, kind, description, url, resume_hint, created_at FROM human_tasks "
        "WHERE state = 'open' ORDER BY created_at, id"
    ).fetchall()
    return TaskList(open_count=len(rows), tasks=[HumanTask.model_validate(r) for r in rows])
