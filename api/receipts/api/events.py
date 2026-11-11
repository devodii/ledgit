from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from receipts.api.queries import STATUS_EXPR
from receipts.db.connection import Conn, get_conn
from receipts.models.api import EventSummary, StatusCount, TypeCount

router = APIRouter(tags=["events"])


@router.get("/events/{slug}/summary", operation_id="getEventSummary")
def event_summary(slug: str, conn: Annotated[Conn, Depends(get_conn)]) -> EventSummary:
    event = conn.execute("SELECT * FROM events WHERE slug = %s", (slug,)).fetchone()
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    by_status = conn.execute(
        f"""
        SELECT {STATUS_EXPR} AS status, count(*)::int AS count
        FROM claims c LEFT JOIN verdicts v ON v.claim_id = c.id
        WHERE c.event_slug = %s GROUP BY 1 ORDER BY 1
        """,
        (slug,),
    ).fetchall()
    by_type = conn.execute(
        "SELECT claim_type, count(*)::int AS count FROM claims WHERE event_slug = %s "
        "GROUP BY 1 ORDER BY 1",
        (slug,),
    ).fetchall()
    return EventSummary(
        slug=event["slug"],
        name=event["name"],
        location=event["location"],
        window_start=event["window_start"],
        window_end=event["window_end"],
        total=sum(r["count"] for r in by_status),
        by_status=[StatusCount.model_validate(r) for r in by_status],
        by_type=[TypeCount.model_validate(r) for r in by_type],
    )
