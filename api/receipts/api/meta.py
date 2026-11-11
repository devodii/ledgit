import hashlib
from typing import Annotated

from fastapi import APIRouter, Depends

from receipts.db.connection import Conn, get_conn
from receipts.models.api import Health, Meta

router = APIRouter(tags=["meta"])


@router.get("/health", operation_id="getHealth")
def health() -> Health:
    return Health(status="ok")


@router.get("/meta", operation_id="getMeta")
def meta(conn: Annotated[Conn, Depends(get_conn)]) -> Meta:
    row = conn.execute(
        """
        SELECT (SELECT max(checked_at) FROM verdicts) AS last_verified_at,
               (SELECT count(*) FROM claims) AS claims,
               (SELECT max(created_at) FROM claims) AS latest_claim,
               (SELECT count(*) FROM verdict_changes) AS changes
        """
    ).fetchone()
    assert row is not None
    fingerprint = (
        f"{row['claims']}|{row['latest_claim']}|{row['changes']}|{row['last_verified_at']}"
    )
    return Meta(
        last_verified_at=row["last_verified_at"],
        data_version=hashlib.sha256(fingerprint.encode()).hexdigest()[:12],
    )
