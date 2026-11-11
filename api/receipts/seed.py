import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from receipts.db.connection import connect
from receipts.models.enums import ObservationResult, VerdictStatus
from receipts.registry.loader import (
    read_event_seed,
    read_registry,
    sync_event,
    sync_registry,
)


class FixtureObservation(BaseModel):
    evidence: str
    result: ObservationResult
    detail: dict[str, Any] = {}


class FixtureVerdict(BaseModel):
    claim: str
    status: VerdictStatus
    reason: str
    observations: list[FixtureObservation] = []
    history: list[dict[str, str | None]] = []


def seed_fixtures(directory: Path) -> dict[str, int]:
    event = read_event_seed(directory / "event.yaml")
    entries = read_registry(directory / "registry.yaml")
    verdicts = [
        FixtureVerdict.model_validate(v)
        for v in yaml.safe_load((directory / "verdicts.yaml").read_text())
    ]
    with connect() as conn:
        sync_event(conn, event)
        sync_registry(conn, entries)
        conn.execute(
            "DELETE FROM verdicts WHERE claim_id = ANY(%s)", ([v.claim for v in verdicts],)
        )
        conn.execute(
            "DELETE FROM verdict_changes WHERE claim_id = ANY(%s)", ([v.claim for v in verdicts],)
        )
        for verdict in verdicts:
            for obs in verdict.observations:
                row = conn.execute(
                    "SELECT id FROM evidence WHERE claim_id = %s AND ref = %s",
                    (verdict.claim, obs.evidence),
                ).fetchone()
                if row is None:
                    raise ValueError(f"fixture references unknown evidence {obs.evidence}")
                conn.execute("DELETE FROM observations WHERE evidence_id = %s", (row["id"],))
                conn.execute(
                    "INSERT INTO observations (evidence_id, result, detail) "
                    "VALUES (%s, %s, %s::jsonb)",
                    (row["id"], obs.result, _json(obs.detail)),
                )
            conn.execute(
                "INSERT INTO verdicts (claim_id, status, reason) VALUES (%s, %s, %s)",
                (verdict.claim, verdict.status, verdict.reason),
            )
            transitions = verdict.history or [{"from": None, "to": verdict.status.value}]
            for step in transitions:
                conn.execute(
                    "INSERT INTO verdict_changes (claim_id, from_status, to_status, reason) "
                    "VALUES (%s, %s, %s, %s)",
                    (verdict.claim, step.get("from"), step["to"], verdict.reason),
                )
        conn.commit()
    return {"claims": len(entries), "verdicts": len(verdicts)}


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value)
