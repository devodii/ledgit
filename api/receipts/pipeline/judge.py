import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from pydantic import ValidationError

from receipts.connectors.youtube import YouTubeConnector
from receipts.db.connection import connect
from receipts.llm import LLMError, LLMProvider, get_provider
from receipts.models.pipeline import Candidate, JudgeBatch
from receipts.models.registry import EventSeed
from receipts.pipeline.common import stage_cache, write_report

JUDGE_VERSION = "v1"

SYSTEM = """You are a skeptical fact-check editor reviewing claims that another system extracted from a conference talk transcript. A wrong or invented claim would destroy the credibility of a public site, so you reject anything doubtful.

For each numbered candidate decide, using only the transcript, video title and description provided:
- "checkable": true only if the quote is a specific statement about something that will launch, has launched, or is needed on Stellar, naming a product, asset, corridor, feature or date, and could be checked against public data. False for vision statements, marketing language, generalities, or anything not about Stellar.
- "summary_faithful": true only if the summary says nothing the quote does not support.
- "org_correct": true only if the named organisation is the one the statement is actually about, according to the transcript.
- "type_correct": true if claim_type fits (partner_launch: a named company launching or integrating on Stellar; roadmap: a named product or feature planned or shipping; protocol_feature: a change to the Stellar protocol or core software; open_ask: the speaker asks for something to be built and no builder is named).
- "speaker_correct": true or false if a speaker name is given and you can tell from the text, otherwise null.
- "confidence": 0 to 1, how confident you are that this is a good, accurate, checkable claim.
- "issue": one short sentence if anything is wrong or weak, else empty.

Reply with JSON only: {"verdicts":[{"index":0,"checkable":true,"summary_faithful":true,"org_correct":true,"type_correct":true,"speaker_correct":null,"confidence":0.0,"issue":""}]}
Return one verdict per candidate, in order."""


def build_prompt(title: str, description: str, transcript: str, candidates: list[Candidate]) -> str:
    listing = "\n".join(
        f"[{i}] claim_type={c.claim_type.value} | org={c.org_name} | "
        f"speaker={c.speaker_name or '-'} ({c.speaker_role or '-'}) | quote: {c.quote} | "
        f"summary: {c.summary}"
        for i, c in enumerate(candidates)
    )
    return (
        f"VIDEO TITLE: {title}\n\nVIDEO DESCRIPTION:\n{description[:1500]}\n\n"
        f"CANDIDATES:\n{listing}\n\nTRANSCRIPT:\n{transcript}"
    )


def parse_judge(raw: str) -> JudgeBatch:
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in judge output")
    return JudgeBatch.model_validate(json.loads(cleaned[start : end + 1]))


def judge_talk(
    provider: LLMProvider, talk: dict[str, Any], candidates: list[Candidate]
) -> list[Candidate | None]:
    prompt = build_prompt(talk["title"], talk["description"], talk["full_text"][:90000], candidates)
    batch: JudgeBatch | None = None
    for _ in range(2):
        try:
            batch = parse_judge(provider.complete(SYSTEM, prompt))
            break
        except (ValueError, ValidationError, LLMError):
            continue
    verdicts = {v.index: v for v in (batch.verdicts if batch else [])}
    out: list[Candidate | None] = []
    for index, candidate in enumerate(candidates):
        verdict = verdicts.get(index)
        if verdict is None:
            candidate.judge_issue = "judge_unavailable"
            out.append(None)
            continue
        candidate.judge_confidence = verdict.confidence
        candidate.judge_issue = verdict.issue
        passed = (
            verdict.checkable
            and verdict.summary_faithful
            and verdict.org_correct
            and verdict.speaker_correct is not False
        )
        out.append(candidate if passed else None)
        if not passed:
            candidate.judge_issue = candidate.judge_issue or _reason(verdict)
    return out


def _reason(verdict: Any) -> str:
    if not verdict.checkable:
        return "not_checkable"
    if not verdict.summary_faithful:
        return "summary_not_faithful"
    if not verdict.org_correct:
        return "org_incorrect"
    return "speaker_incorrect"


def run_judge(seed: EventSeed, workers: int = 4) -> int:
    provider = get_provider()
    cache = stage_cache("judge")
    candidates = [
        Candidate.model_validate(c)
        for c in json.loads((stage_cache("candidates") / f"{seed.slug}.json").read_text())
    ]
    by_video: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        by_video.setdefault(candidate.video_id, []).append(candidate)
    youtube = YouTubeConnector()
    with connect() as conn:
        rows = conn.execute(
            "SELECT t.video_id, t.title, tr.full_text, tr.sha256 FROM talks t "
            "JOIN transcripts tr ON tr.video_id = t.video_id WHERE t.event_slug = %s",
            (seed.slug,),
        ).fetchall()
    talks = {r["video_id"]: r for r in rows}

    def work(video_id: str) -> tuple[list[Candidate], dict[str, int]]:
        group = by_video[video_id]
        talk = dict(talks[video_id])
        key = hashlib.sha256(
            f"{talk['sha256']}|{JUDGE_VERSION}|{provider.name}|"
            f"{'|'.join(c.quote for c in group)}".encode()
        ).hexdigest()[:20]
        path = cache / f"{video_id}-{key}.json"
        drops: dict[str, int] = {}
        if path.is_file():
            data = json.loads(path.read_text())
            kept = [Candidate.model_validate(c) for c in data["kept"]]
            return kept, data["drops"]
        talk["description"] = youtube.metadata(video_id).description
        results = judge_talk(provider, talk, group)
        kept = [c for c in results if c is not None]
        for original, result in zip(group, results, strict=True):
            if result is None:
                reason = original.judge_issue or "rejected"
                drops[reason] = drops.get(reason, 0) + 1
        path.write_text(
            json.dumps({"kept": [c.model_dump(mode="json") for c in kept], "drops": drops})
        )
        return kept, drops

    kept_all: list[Candidate] = []
    drops_total: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for kept, drops in pool.map(work, sorted(by_video)):
            kept_all.extend(kept)
            for reason, count in drops.items():
                drops_total[f"judge:{reason}"] = drops_total.get(f"judge:{reason}", 0) + count
    kept_all.sort(key=lambda c: (c.video_id, c.start_seconds))
    out = stage_cache("judged") / f"{seed.slug}.json"
    out.write_text(json.dumps([c.model_dump(mode="json") for c in kept_all], indent=1))
    write_report(
        "judge",
        seed.slug,
        len(candidates),
        len(kept_all),
        drops_total,
        [f"provider={provider.name} model={provider.model} prompt={JUDGE_VERSION}"],
    )
    return len(kept_all)
