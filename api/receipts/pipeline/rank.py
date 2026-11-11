import json
import re
from difflib import SequenceMatcher

from receipts.connectors.transcripts import normalize
from receipts.models.pipeline import Candidate
from receipts.models.registry import EventSeed
from receipts.pipeline.common import stage_cache, write_report
from receipts.pipeline.resolve import claim_key

SPECIFIC_RE = re.compile(
    r"\b(20\d\d|q[1-4]|\d+(?:\.\d+)?\s?(?:%|percent|million|billion|k)|protocol \d+)\b", re.I
)


def score(candidate: Candidate) -> float:
    base = 0.5 * candidate.specificity + 0.5 * candidate.verifiability
    if candidate.judge_confidence is not None:
        base = 0.6 * candidate.judge_confidence + 0.4 * base
    bonus = 0.0
    if candidate.org_domain:
        bonus += 0.05
    if SPECIFIC_RE.search(candidate.quote):
        bonus += 0.05
    return round(min(base + bonus, 1.0), 3)


def is_duplicate(a: Candidate, b: Candidate) -> bool:
    if SequenceMatcher(None, normalize(a.quote).lower(), normalize(b.quote).lower()).ratio() > 0.85:
        return True
    same_subject = a.org_name.lower() == b.org_name.lower() and a.claim_type == b.claim_type
    return (
        same_subject and SequenceMatcher(None, a.summary.lower(), b.summary.lower()).ratio() > 0.8
    )


def run_rank(seed: EventSeed) -> int:
    path = stage_cache("judged") / f"{seed.slug}.json"
    candidates = [Candidate.model_validate(c) for c in json.loads(path.read_text())]
    for candidate in candidates:
        candidate.score = score(candidate)
        extras = stage_cache("resolve-claims") / f"{claim_key(candidate)}.json"
        has_evidence = extras.is_file() and bool(json.loads(extras.read_text())["evidence"])
        if has_evidence or candidate.protocol_version or candidate.core_version:
            candidate.score = round(min(candidate.score + 0.12, 1.0), 3)
    ranked = sorted(candidates, key=lambda c: (-c.score, c.video_id, c.start_seconds))
    drops: dict[str, int] = {}
    kept: list[Candidate] = []
    per_talk: dict[str, int] = {}
    for candidate in ranked:
        if any(is_duplicate(candidate, other) for other in kept):
            drops["duplicate"] = drops.get("duplicate", 0) + 1
            continue
        if per_talk.get(candidate.video_id, 0) >= seed.limits.max_claims_per_talk:
            drops["over_talk_cap"] = drops.get("over_talk_cap", 0) + 1
            continue
        if len(kept) >= seed.limits.target_claims:
            drops["over_target"] = drops.get("over_target", 0) + 1
            continue
        per_talk[candidate.video_id] = per_talk.get(candidate.video_id, 0) + 1
        kept.append(candidate)
    out = stage_cache("ranked") / f"{seed.slug}.json"
    out.write_text(json.dumps([c.model_dump(mode="json") for c in kept], indent=1))
    write_report("rank", seed.slug, len(candidates), len(kept), drops)
    return len(kept)
