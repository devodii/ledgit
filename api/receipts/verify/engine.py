import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from receipts.db.connection import connect
from receipts.models.enums import ClaimType, VerdictStatus
from receipts.settings import get_settings
from receipts.verify.checkers import Checkers, Observation
from receipts.verify.verdict import EvidenceResult, compute_verdict


def run_verify() -> str:
    settings = get_settings()
    checkers = Checkers()
    with connect() as conn:
        evidence = conn.execute(
            "SELECT id, claim_id, kind::text AS kind, ref FROM evidence ORDER BY id"
        ).fetchall()
        claims = conn.execute(
            """
            SELECT c.id, c.claim_type::text AS claim_type, t.published_at,
                   v.status::text AS previous
            FROM claims c
            LEFT JOIN talks t ON t.video_id = c.video_id
            LEFT JOIN verdicts v ON v.claim_id = c.id
            ORDER BY c.id
            """
        ).fetchall()

        def check(row: dict[str, object]) -> tuple[dict[str, object], Observation]:
            return row, checkers.run(str(row["kind"]), str(row["ref"]))

        with ThreadPoolExecutor(max_workers=4) as pool:
            checked = list(pool.map(check, evidence))
        by_claim: dict[str, list[EvidenceResult]] = {}
        for row, observation in checked:
            conn.execute(
                "INSERT INTO observations (evidence_id, result, detail) VALUES (%s, %s, %s::jsonb)",
                (
                    row["id"],
                    observation.result,
                    json.dumps({"summary": observation.summary, **observation.detail}),
                ),
            )
            by_claim.setdefault(str(row["claim_id"]), []).append(
                EvidenceResult(
                    label=f"{row['kind']} {str(row['ref'])[:24]}",
                    result=observation.result,
                    summary=observation.summary,
                )
            )
        now = datetime.now(UTC)
        changed = 0
        for claim in claims:
            published = claim["published_at"]
            age = (now - published).days if published else None
            previous = VerdictStatus(claim["previous"]) if claim["previous"] else None
            status, reason = compute_verdict(
                ClaimType(claim["claim_type"]),
                age,
                by_claim.get(str(claim["id"]), []),
                previous,
                settings.verify_pending_days,
            )
            conn.execute(
                """
                INSERT INTO verdicts (claim_id, status, reason, checked_at)
                VALUES (%s, %s, %s, now())
                ON CONFLICT (claim_id) DO UPDATE SET
                    status = EXCLUDED.status, reason = EXCLUDED.reason,
                    checked_at = EXCLUDED.checked_at
                """,
                (claim["id"], status, reason),
            )
            if previous != status:
                changed += 1
                conn.execute(
                    "INSERT INTO verdict_changes (claim_id, from_status, to_status, reason) "
                    "VALUES (%s, %s, %s, %s)",
                    (claim["id"], previous, status, reason),
                )
        conn.commit()
    return f"verified {len(claims)} claims, {len(checked)} checks, {changed} verdict changes"
