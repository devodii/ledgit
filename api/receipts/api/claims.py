from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from receipts.api.queries import (
    CLAIM_SUMMARY_SELECT,
    STATUS_EXPR,
    decode_cursor,
    encode_cursor,
)
from receipts.db.connection import Conn, get_conn
from receipts.models.api import (
    ClaimDetail,
    ClaimPage,
    ClaimSummary,
    EvidenceOut,
    ObservationOut,
    OrgOut,
    ScfOut,
    SourceOut,
    VerdictChangeOut,
    VerdictOut,
    VideoOut,
)
from receipts.models.enums import ClaimType, VerdictStatus

router = APIRouter(tags=["claims"])


def _summary(row: dict[str, Any]) -> ClaimSummary:
    return ClaimSummary.model_validate(row)


@router.get("/claims", operation_id="listClaims")
def list_claims(
    conn: Annotated[Conn, Depends(get_conn)],
    status: VerdictStatus | None = None,
    claim_type: ClaimType | None = None,
    country: str | None = None,
    org: str | None = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    sort: Literal["newest", "oldest"] = "newest",
    limit: Annotated[int, Query(ge=1, le=100)] = 24,
    cursor: str | None = None,
) -> ClaimPage:
    where: list[str] = []
    params: dict[str, Any] = {}
    if status:
        where.append(f"{STATUS_EXPR} = %(status)s::verdict_status")
        params["status"] = status.value
    if claim_type:
        where.append("c.claim_type = %(claim_type)s::claim_type")
        params["claim_type"] = claim_type.value
    if country:
        where.append("lower(o.country) = lower(%(country)s)")
        params["country"] = country
    if org:
        where.append("o.slug = %(org)s")
        params["org"] = org
    if q:
        where.append(
            "(c.quote ILIKE %(q)s OR c.summary ILIKE %(q)s OR o.name ILIKE %(q)s "
            "OR c.speaker_name ILIKE %(q)s)"
        )
        params["q"] = f"%{q}%"
    if cursor:
        try:
            created_at, claim_id = decode_cursor(cursor)
            created = datetime.fromisoformat(created_at)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail="invalid cursor") from exc
        op = "<" if sort == "newest" else ">"
        where.append(f"(c.created_at, c.id) {op} (%(cur_at)s, %(cur_id)s)")
        params.update(cur_at=created, cur_id=claim_id)
    direction = "DESC" if sort == "newest" else "ASC"
    sql = CLAIM_SUMMARY_SELECT
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += f" ORDER BY c.created_at {direction}, c.id {direction} LIMIT %(limit)s"
    params["limit"] = limit + 1
    rows = conn.execute(sql, params).fetchall()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None
    return ClaimPage(items=[_summary(r) for r in rows], next_cursor=next_cursor)


@router.get("/claims/{claim_id}", operation_id="getClaim")
def get_claim(claim_id: str, conn: Annotated[Conn, Depends(get_conn)]) -> ClaimDetail:
    row = conn.execute(
        f"""
        SELECT c.*, o.slug AS o_slug, o.name AS o_name, o.domain AS o_domain,
               o.country AS o_country, v.status AS v_status, v.reason AS v_reason,
               v.checked_at AS v_checked_at, {STATUS_EXPR} AS status
        FROM claims c
        JOIN orgs o ON o.slug = c.org_slug
        LEFT JOIN verdicts v ON v.claim_id = c.id
        WHERE c.id = %s
        """,
        (claim_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="claim not found")
    evidence_rows = conn.execute(
        """
        SELECT e.id, e.kind, e.network, e.ref, e.found_via,
               ob.checked_at AS ob_checked_at, ob.result AS ob_result, ob.detail AS ob_detail
        FROM evidence e
        LEFT JOIN LATERAL (
            SELECT checked_at, result, detail FROM observations
            WHERE evidence_id = e.id ORDER BY checked_at DESC, id DESC LIMIT 1
        ) ob ON TRUE
        WHERE e.claim_id = %s ORDER BY e.id
        """,
        (claim_id,),
    ).fetchall()
    history_rows = conn.execute(
        "SELECT claim_id, from_status, to_status, reason, changed_at FROM verdict_changes "
        "WHERE claim_id = %s ORDER BY changed_at DESC, id DESC",
        (claim_id,),
    ).fetchall()
    evidence = [
        EvidenceOut(
            id=e["id"],
            kind=e["kind"],
            network=e["network"],
            ref=e["ref"],
            found_via=e["found_via"],
            latest_observation=(
                ObservationOut(
                    checked_at=e["ob_checked_at"], result=e["ob_result"], detail=e["ob_detail"]
                )
                if e["ob_checked_at"]
                else None
            ),
        )
        for e in evidence_rows
    ]
    reason = row["v_reason"] or (
        "Requested on stage, no builder identified."
        if row["claim_type"] == "open_ask"
        else "Not yet checked."
    )
    return ClaimDetail(
        id=row["id"],
        event=row["event_slug"],
        claim_type=row["claim_type"],
        quote=row["quote"],
        summary=row["summary"],
        speaker_name=row["speaker_name"],
        speaker_role=row["speaker_role"],
        org=OrgOut(
            slug=row["o_slug"], name=row["o_name"], domain=row["o_domain"], country=row["o_country"]
        ),
        video=VideoOut(
            id=row["video_id"],
            url=row["video_url"],
            start_seconds=row["start_seconds"],
            caption_source=row["caption_source"],
        ),
        scf=ScfOut(
            found=row["scf_found"],
            project_url=row["scf_project_url"],
            awarded_usd=row["scf_awarded_usd"],
        ),
        evidence=evidence,
        verdict=VerdictOut(status=row["status"], reason=reason, checked_at=row["v_checked_at"]),
        history=[VerdictChangeOut.model_validate(h) for h in history_rows],
        extractor_model=row["extractor_model"],
        confidence=row["confidence"],
        sources=[SourceOut.model_validate(x) for x in row["sources"]],
        domain_source=row["domain_source"],
        country_source=row["country_source"],
        scf_source=row["scf_source"],
        transcript_sha256=row["transcript_sha256"],
    )
