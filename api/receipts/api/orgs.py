from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from receipts.api.queries import CLAIM_SUMMARY_SELECT
from receipts.db.connection import Conn, get_conn
from receipts.models.api import ClaimSummary, OrgDetail, OrgOut, OrgSummary

router = APIRouter(tags=["orgs"])


@router.get("/orgs", operation_id="listOrgs")
def list_orgs(conn: Annotated[Conn, Depends(get_conn)]) -> list[OrgSummary]:
    rows = conn.execute(
        """
        SELECT o.slug, o.name, o.domain, o.country, count(c.id)::int AS claim_count
        FROM orgs o LEFT JOIN claims c ON c.org_slug = o.slug
        GROUP BY o.slug ORDER BY o.name
        """
    ).fetchall()
    return [OrgSummary.model_validate(r) for r in rows]


@router.get("/orgs/{slug}", operation_id="getOrg")
def get_org(slug: str, conn: Annotated[Conn, Depends(get_conn)]) -> OrgDetail:
    org = conn.execute(
        "SELECT slug, name, domain, country FROM orgs WHERE slug = %s", (slug,)
    ).fetchone()
    if org is None:
        raise HTTPException(status_code=404, detail="organisation not found")
    claims = conn.execute(
        CLAIM_SUMMARY_SELECT + " WHERE o.slug = %s ORDER BY c.created_at DESC, c.id DESC", (slug,)
    ).fetchall()
    return OrgDetail(
        org=OrgOut.model_validate(org), claims=[ClaimSummary.model_validate(c) for c in claims]
    )
