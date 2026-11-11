import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from receipts.connectors.transcripts import normalize
from receipts.db.connection import connect
from receipts.models.pipeline import Candidate
from receipts.registry.loader import read_registry
from receipts.settings import get_settings


class Funnel(BaseModel):
    videos_discovered: int
    transcripts_fetched: int
    manual_captions: int
    auto_captions: int
    candidates_extracted: int
    judge_accepted: int
    ranked_kept: int
    public_registry: int
    review_queue: int


class QuoteAudit(BaseModel):
    checked: int
    verbatim: int
    failures: list[str] = Field(default_factory=list)


class JudgeStats(BaseModel):
    mean_confidence_accepted: float
    confidence_buckets: dict[str, int]
    extractor_high_score_accepted_rate: float | None


class Coverage(BaseModel):
    claims: int
    speaker_named: float
    domain_resolved: float
    country_known: float
    scf_found: float
    with_evidence: float
    protocol_evidence: int
    claim_types: dict[str, int]
    evidence_kinds: dict[str, int]
    sources: dict[str, int]
    caption_source: dict[str, int]


class VerdictStats(BaseModel):
    verdicts: dict[str, int]
    observations: dict[str, int]
    changes: int


class HumanReview(BaseModel):
    labelled: int
    correct: int
    precision: float | None


class EvalReport(BaseModel):
    event: str
    generated_at: datetime
    provider: str
    funnel: Funnel
    drops: dict[str, dict[str, int]]
    quote_audit: QuoteAudit
    judge: JudgeStats
    coverage: Coverage
    verdicts: VerdictStats
    human_review: HumanReview
    per_talk: list[dict[str, Any]]


def _load(path: Path) -> Any:
    return json.loads(path.read_text()) if path.is_file() else []


def _rate(part: int, whole: int) -> float:
    return round(part / whole, 3) if whole else 0.0


def build_report(event: str) -> EvalReport:
    settings = get_settings()
    reports = settings.data_dir / "reports" / event
    cache = settings.cache_dir
    stage = {p.stem: json.loads(p.read_text()) for p in reports.glob("*.json")}
    candidates = [
        Candidate.model_validate(c) for c in _load(cache / "candidates" / f"{event}.json")
    ]
    judged = [Candidate.model_validate(c) for c in _load(cache / "judged" / f"{event}.json")]
    registry = read_registry(settings.data_dir / "registry" / f"{event}.yaml")
    review_path = settings.data_dir / "review" / f"{event}.yaml"
    review = read_registry(review_path) if review_path.is_file() else []

    with connect() as conn:
        transcripts = {
            r["video_id"]: r
            for r in conn.execute(
                "SELECT t.video_id, t.title, tr.full_text, tr.caption_source::text AS src "
                "FROM talks t JOIN transcripts tr ON tr.video_id = t.video_id "
                "WHERE t.event_slug = %s",
                (event,),
            ).fetchall()
        }
        verdict_rows = conn.execute(
            "SELECT v.status::text AS k, count(*)::int AS n FROM verdicts v "
            "JOIN claims c ON c.id = v.claim_id WHERE c.event_slug = %s GROUP BY 1",
            (event,),
        ).fetchall()
        obs_rows = conn.execute(
            "SELECT o.result::text AS k, count(*)::int AS n FROM observations o "
            "JOIN evidence e ON e.id = o.evidence_id JOIN claims c ON c.id = e.claim_id "
            "WHERE c.event_slug = %s GROUP BY 1",
            (event,),
        ).fetchall()
        changes = conn.execute(
            "SELECT count(*)::int AS n FROM verdict_changes vc JOIN claims c ON c.id = vc.claim_id "
            "WHERE c.event_slug = %s",
            (event,),
        ).fetchone()

    captions = Counter(t["src"] for t in transcripts.values())
    funnel = Funnel(
        videos_discovered=stage.get("discover", {}).get("counts_in", 0),
        transcripts_fetched=len(transcripts),
        manual_captions=captions.get("manual", 0),
        auto_captions=captions.get("auto", 0),
        candidates_extracted=len(candidates),
        judge_accepted=len(judged),
        ranked_kept=stage.get("rank", {}).get("counts_out", 0),
        public_registry=len(registry),
        review_queue=len(review),
    )

    failures: list[str] = []
    for entry in registry:
        text = (
            normalize(transcripts[entry.claim.video.id]["full_text"])
            if entry.claim.video.id in transcripts
            else ""
        )
        if normalize(entry.claim.quote) not in text:
            failures.append(entry.id)
    audit = QuoteAudit(
        checked=len(registry), verbatim=len(registry) - len(failures), failures=failures
    )

    buckets: Counter[str] = Counter()
    for c in judged:
        low = int((c.judge_confidence or 0) * 5) / 5
        buckets[f"{low:.1f}-{min(low + 0.2, 1.0):.1f}"] += 1
    high = [c for c in candidates if c.specificity >= 0.8 and c.verifiability >= 0.8]
    judged_quotes = {c.quote for c in judged}
    judge = JudgeStats(
        mean_confidence_accepted=round(
            sum(c.judge_confidence or 0 for c in judged) / len(judged), 3
        )
        if judged
        else 0.0,
        confidence_buckets=dict(sorted(buckets.items())),
        extractor_high_score_accepted_rate=_rate(
            sum(1 for c in high if c.quote in judged_quotes), len(high)
        )
        if high
        else None,
    )

    n = len(registry)
    kinds = Counter(e.kind.value for entry in registry for e in entry.evidence)
    sources = Counter(s.name for entry in registry for s in entry.sources)
    coverage = Coverage(
        claims=n,
        speaker_named=_rate(sum(1 for e in registry if e.claim.speaker.name), n),
        domain_resolved=_rate(sum(1 for e in registry if e.claim.org.domain), n),
        country_known=_rate(sum(1 for e in registry if e.claim.org.country), n),
        scf_found=_rate(sum(1 for e in registry if e.backing.scf.found), n),
        with_evidence=_rate(sum(1 for e in registry if e.evidence), n),
        protocol_evidence=kinds.get("protocol_upgrade", 0),
        claim_types=dict(Counter(e.claim.type.value for e in registry)),
        evidence_kinds=dict(kinds),
        sources=dict(sources),
        caption_source=dict(Counter(e.claim.caption_source.value for e in registry)),
    )

    per_talk = []
    by_talk_cand = Counter(c.video_id for c in candidates)
    by_talk_judged = Counter(c.video_id for c in judged)
    by_talk_public = Counter(e.claim.video.id for e in registry)
    for vid, row in sorted(transcripts.items(), key=lambda kv: -by_talk_public.get(kv[0], 0)):
        per_talk.append(
            {
                "video_id": vid,
                "title": row["title"],
                "candidates": by_talk_cand.get(vid, 0),
                "judge_accepted": by_talk_judged.get(vid, 0),
                "public": by_talk_public.get(vid, 0),
            }
        )

    labels = _read_labels(settings.evals_dir / event / "review-sample.yaml")
    labelled = [v for v in labels if v in ("correct", "incorrect", "partial")]
    human = HumanReview(
        labelled=len(labelled),
        correct=labelled.count("correct"),
        precision=_rate(labelled.count("correct"), len(labelled)) if labelled else None,
    )

    return EvalReport(
        event=event,
        generated_at=datetime.now(UTC),
        provider=" ".join(stage.get("extract", {}).get("notes", [])[:1]),
        funnel=funnel,
        drops={k: v.get("drops", {}) for k, v in stage.items() if v.get("drops")},
        quote_audit=audit,
        judge=judge,
        coverage=coverage,
        verdicts=VerdictStats(
            verdicts={r["k"]: r["n"] for r in verdict_rows},
            observations={r["k"]: r["n"] for r in obs_rows},
            changes=int(changes["n"]) if changes else 0,
        ),
        human_review=human,
        per_talk=per_talk,
    )


def _read_labels(path: Path) -> list[str]:
    if not path.is_file():
        return []
    items = yaml.safe_load(path.read_text()) or []
    return [str(i.get("human_label")) for i in items if i.get("human_label")]


def write_review_sample(event: str, size: int = 20) -> Path:
    settings = get_settings()
    target = settings.evals_dir / event / "review-sample.yaml"
    if target.is_file():
        return target
    registry = read_registry(settings.data_dir / "registry" / f"{event}.yaml")
    ordered = sorted(registry, key=lambda e: hashlib.sha256(e.id.encode()).hexdigest())[:size]
    items = [
        {
            "id": e.id,
            "org": e.claim.org.name,
            "claim_type": e.claim.type.value,
            "quote": e.claim.quote,
            "summary": e.claim.summary,
            "watch": e.claim.video.url_at_timestamp,
            "human_label": None,
            "note": "",
        }
        for e in ordered
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Fill human_label with one of: correct, partial, incorrect.\n"
        "# Open the watch link, listen to the quote, check org and summary.\n"
        "# Then run `receipts eval --event <slug>` to get a precision estimate.\n"
    )
    target.write_text(
        header + yaml.safe_dump(items, sort_keys=False, allow_unicode=True, width=1000)
    )
    return target


def pct(value: float | None) -> str:
    return f"{(value or 0) * 100:.0f}%"


def render_markdown(r: EvalReport) -> str:
    f, a, j, c, v, h = r.funnel, r.quote_audit, r.judge, r.coverage, r.verdicts, r.human_review
    lines = [
        f"# Eval report: {r.event}",
        "",
        f"Generated {r.generated_at:%Y-%m-%d %H:%M} UTC. Extraction and judging: `{r.provider}`.",
        "",
        "## Funnel",
        "",
        "| Stage | Count |",
        "| --- | ---: |",
        f"| Videos discovered | {f.videos_discovered} |",
        f"| Transcripts fetched | {f.transcripts_fetched} ({f.manual_captions} manual, {f.auto_captions} auto) |",
        f"| Candidate claims extracted | {f.candidates_extracted} |",
        f"| Accepted by the judge | {f.judge_accepted} |",
        f"| Kept after rank and trim | {f.ranked_kept} |",
        f"| Public registry | {f.public_registry} |",
        f"| Review queue | {f.review_queue} |",
        "",
        "## Quote integrity",
        "",
        f"Independent re-check of every public quote against the stored transcript: "
        f"**{a.verbatim} of {a.checked} verbatim**"
        + (f". Failures: {', '.join(a.failures)}" if a.failures else "."),
        "",
        "## Judge",
        "",
        f"Mean judge confidence on accepted claims: **{j.mean_confidence_accepted}**.",
        "",
        "| Confidence | Claims |",
        "| --- | ---: |",
        *[f"| {k} | {n} |" for k, n in j.confidence_buckets.items()],
        "",
        (
            f"Of candidates the extractor scored 0.8 or higher on both specificity and "
            f"verifiability, the judge accepted **{pct(j.extractor_high_score_accepted_rate)}**."
            if j.extractor_high_score_accepted_rate is not None
            else "No candidate scored 0.8 or higher on both axes."
        ),
        "",
        "## Drops by stage",
        "",
        "| Stage | Reason | Count |",
        "| --- | --- | ---: |",
        *[f"| {s} | {k} | {n} |" for s, d in r.drops.items() for k, n in d.items()],
        "",
        "## Coverage of the public registry",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Speaker named | {pct(c.speaker_named)} |",
        f"| Domain resolved | {pct(c.domain_resolved)} |",
        f"| Country known | {pct(c.country_known)} |",
        f"| SCF award found | {pct(c.scf_found)} |",
        f"| At least one evidence item | {pct(c.with_evidence)} |",
        "",
        "Claim types: " + ", ".join(f"{k} {n}" for k, n in sorted(c.claim_types.items())),
        "",
        "Evidence kinds: "
        + (", ".join(f"{k} {n}" for k, n in sorted(c.evidence_kinds.items())) or "none"),
        "",
        "Where facts came from (claims citing each source): "
        + (", ".join(f"{k} {n}" for k, n in sorted(c.sources.items())) or "none"),
        "",
        "Caption source: " + ", ".join(f"{k} {n}" for k, n in sorted(c.caption_source.items())),
        "",
        "## Verification",
        "",
        "Verdicts: "
        + (", ".join(f"{k} {n}" for k, n in sorted(v.verdicts.items())) or "not run yet"),
        "",
        "Check outcomes: "
        + (", ".join(f"{k} {n}" for k, n in sorted(v.observations.items())) or "not run yet"),
        "",
        f"Verdict changes recorded: {v.changes}",
        "",
        "## Human review",
        "",
        (
            f"{h.labelled} claims labelled, {h.correct} correct, precision **{pct(h.precision)}**."
            if h.precision is not None
            else "No labels yet. Fill `review-sample.yaml` and rerun to get a precision estimate."
        ),
        "",
        "## Yield per talk",
        "",
        "| Talk | Candidates | Judge accepted | Public |",
        "| --- | ---: | ---: | ---: |",
        *[
            f"| {t['title'][:70]} | {t['candidates']} | {t['judge_accepted']} | {t['public']} |"
            for t in r.per_talk
        ],
        "",
    ]
    return "\n".join(lines)


def run_eval(event: str) -> Path:
    settings = get_settings()
    write_review_sample(event)
    report = build_report(event)
    target = settings.evals_dir / event
    target.mkdir(parents=True, exist_ok=True)
    (target / "report.json").write_text(report.model_dump_json(indent=2))
    (target / "report.md").write_text(render_markdown(report))
    return target / "report.md"
