import base64
import json
from datetime import datetime
from typing import Any

STATUS_EXPR = (
    "COALESCE(v.status, CASE WHEN c.claim_type = 'open_ask' "
    "THEN 'open_ask'::verdict_status ELSE 'pending'::verdict_status END)"
)

CLAIM_SUMMARY_SELECT = f"""
    SELECT c.id, c.event_slug AS event, c.claim_type, {STATUS_EXPR} AS status,
           c.quote, c.summary, c.speaker_name, c.speaker_role,
           o.slug AS org_slug, o.name AS org_name, o.country AS org_country,
           c.video_url, c.video_id, c.start_seconds, c.caption_source,
           c.scf_found, c.scf_awarded_usd, v.checked_at AS last_checked_at, c.created_at
    FROM claims c
    JOIN orgs o ON o.slug = c.org_slug
    LEFT JOIN verdicts v ON v.claim_id = c.id
"""


def encode_cursor(*parts: Any) -> str:
    payload = [p.isoformat() if isinstance(p, datetime) else p for p in parts]
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor: str) -> list[Any]:
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor.encode()))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid cursor") from exc
    if not isinstance(data, list):
        raise ValueError("invalid cursor")
    return data
