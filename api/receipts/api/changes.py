from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from receipts.api.queries import decode_cursor, encode_cursor
from receipts.db.connection import Conn, get_conn
from receipts.models.api import ChangeItem, ChangePage

router = APIRouter(tags=["changes"])


@router.get("/changes", operation_id="listChanges")
def list_changes(
    conn: Annotated[Conn, Depends(get_conn)],
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    cursor: str | None = None,
) -> ChangePage:
    params: dict[str, Any] = {"limit": limit + 1}
    where = ""
    if cursor:
        try:
            changed_at, change_id = decode_cursor(cursor)
            params.update(cur_at=datetime.fromisoformat(changed_at), cur_id=int(change_id))
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail="invalid cursor") from exc
        where = "WHERE (vc.changed_at, vc.id) < (%(cur_at)s, %(cur_id)s)"
    rows = conn.execute(
        f"""
        SELECT vc.id, vc.claim_id, o.name AS org_name, c.summary, vc.from_status,
               vc.to_status, vc.reason, vc.changed_at
        FROM verdict_changes vc
        JOIN claims c ON c.id = vc.claim_id
        JOIN orgs o ON o.slug = c.org_slug
        {where}
        ORDER BY vc.changed_at DESC, vc.id DESC LIMIT %(limit)s
        """,
        params,
    ).fetchall()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(rows[-1]["changed_at"], rows[-1]["id"]) if has_more else None
    return ChangePage(items=[ChangeItem.model_validate(r) for r in rows], next_cursor=next_cursor)
