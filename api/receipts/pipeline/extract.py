import hashlib
import json
import re
from bisect import bisect_right
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from receipts.connectors.transcripts import normalize
from receipts.db.connection import connect
from receipts.llm import LLMError, LLMProvider, get_provider
from receipts.models.enums import CaptionSource
from receipts.models.pipeline import Candidate, RawClaimBatch
from receipts.models.registry import EventSeed
from receipts.models.talks import Segment
from receipts.pipeline.common import stage_cache, write_report

PROMPT_VERSION = "v1"
MAX_CHARS = 60000

SYSTEM = """You extract checkable claims from conference talk transcripts for a public fact-check site about the Stellar network.

A claim is a specific statement about something that will launch, has launched, or is needed on Stellar, that names a product, asset, corridor, feature, or date, and that could be checked against public data.

Reject: vision statements, marketing language, generalities, anything not tied to Stellar, and anything you cannot quote exactly.

Rules you must follow:
- "quote" must be copied character for character from the transcript text, one or two sentences at most. Do not fix grammar, punctuation, casing or filler words. Do not paraphrase. If you cannot copy it exactly, skip the claim.
- "summary" is one neutral sentence describing what was said. Do not add facts.
- "claim_type" is one of: partner_launch (a named company launching or integrating something on Stellar), roadmap (a named product or feature planned or shipping), protocol_feature (a change to the Stellar protocol or core software), open_ask (the speaker asks for something to be built and no builder is named).
- "org_name" is the organisation the claim is about. Only use a name that appears in the transcript, the video title or the video description. Leave it empty if unclear.
- "speaker_name" and "speaker_role" only if stated in the transcript, title or description. Never guess. Leave empty otherwise.
- "org_domain" only if the exact domain is spoken or written in the provided text, else empty.
- "protocol_version" only if the speaker names a specific numbered protocol release, else null.
- "specificity" and "verifiability" are numbers from 0 to 1.
- Return at most N claims, the most specific and checkable ones. Returning none is fine.

Reply with JSON only, no prose, in this shape:
{"claims":[{"quote":"","summary":"","claim_type":"","speaker_name":"","speaker_role":"","org_name":"","org_domain":"","protocol_version":null,"specificity":0.0,"verifiability":0.0}]}"""


def build_prompt(title: str, description: str, text: str, limit: int) -> str:
    return (
        f"N = {limit}\n\nVIDEO TITLE: {title}\n\nVIDEO DESCRIPTION:\n{description[:2000]}\n\n"
        f"TRANSCRIPT:\n{text}"
    )


def parse_batch(raw: str) -> RawClaimBatch:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned, flags=re.M).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return RawClaimBatch.model_validate(json.loads(cleaned[start : end + 1]))


class QuoteLocator:
    def __init__(self, segments: list[Segment]) -> None:
        self.starts: list[int] = []
        self.times: list[float] = []
        parts: list[str] = []
        offset = 0
        for seg in segments:
            text = normalize(seg.text)
            if not text:
                continue
            self.starts.append(offset)
            self.times.append(seg.start)
            parts.append(text)
            offset += len(text) + 1
        self.full_text = " ".join(parts)

    def locate(self, quote: str) -> int | None:
        index = self.full_text.find(normalize(quote))
        if index < 0:
            return None
        position = bisect_right(self.starts, index) - 1
        return max(int(self.times[position]) - 2, 0)


def verify_quote(locator: QuoteLocator, quote: str) -> int | None:
    if len(normalize(quote)) < 25:
        return None
    return locator.locate(quote)


def text_mentions(haystack: str, needle: str) -> bool:
    return bool(needle) and normalize(needle).lower() in normalize(haystack).lower()


def extract_talk(
    provider: LLMProvider, talk: dict[str, Any], limit: int
) -> tuple[list[Candidate], dict[str, int]]:
    drops: dict[str, int] = {}

    def drop(reason: str) -> None:
        drops[reason] = drops.get(reason, 0) + 1

    segments = [Segment.model_validate(s) for s in talk["segments"]]
    locator = QuoteLocator(segments)
    text = locator.full_text
    windows = [text[i : i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)] or [""]
    context = f"{talk['title']}\n{talk['description']}\n{text}"
    out: list[Candidate] = []
    for window in windows:
        prompt = build_prompt(talk["title"], talk["description"], window, limit)
        batch: RawClaimBatch | None = None
        for _ in range(2):
            try:
                batch = parse_batch(provider.complete(SYSTEM, prompt))
                break
            except (ValueError, ValidationError, LLMError):
                continue
        if batch is None:
            drop("llm_output_unusable")
            continue
        for claim in batch.claims:
            start = verify_quote(locator, claim.quote)
            if start is None:
                drop("quote_not_verbatim")
                continue
            if not claim.org_name or not text_mentions(context, claim.org_name):
                drop("org_not_in_source")
                continue
            out.append(
                Candidate(
                    video_id=talk["video_id"],
                    video_title=talk["title"],
                    quote=normalize(claim.quote),
                    summary=claim.summary.strip(),
                    claim_type=claim.claim_type,
                    speaker_name=claim.speaker_name
                    if text_mentions(context, claim.speaker_name)
                    else "",
                    speaker_role=claim.speaker_role
                    if text_mentions(context, claim.speaker_role)
                    else "",
                    org_name=claim.org_name.strip(),
                    org_domain=claim.org_domain.strip().lower()
                    if text_mentions(context, claim.org_domain)
                    else "",
                    protocol_version=claim.protocol_version,
                    start_seconds=start,
                    caption_source=CaptionSource(talk["caption_source"]),
                    transcript_sha256=talk["sha256"],
                    specificity=claim.specificity,
                    verifiability=claim.verifiability,
                    extractor_model=provider.model,
                    extracted_at=datetime.now(UTC),
                )
            )
    return out, drops


def run_extract(seed: EventSeed, workers: int = 4) -> int:
    provider = get_provider()
    cache = stage_cache("extract")
    with connect() as conn:
        talks = conn.execute(
            """
            SELECT t.video_id, t.title, tr.caption_source::text AS caption_source,
                   tr.segments, tr.sha256
            FROM talks t JOIN transcripts tr ON tr.video_id = t.video_id
            WHERE t.event_slug = %s AND t.accepted ORDER BY t.video_id
            """,
            (seed.slug,),
        ).fetchall()
    from receipts.connectors.youtube import YouTubeConnector

    youtube = YouTubeConnector()
    for talk in talks:
        talk["description"] = youtube.metadata(talk["video_id"]).description

    def work(talk: dict[str, Any]) -> tuple[list[Candidate], dict[str, int]]:
        key = hashlib.sha256(
            f"{talk['sha256']}|{PROMPT_VERSION}|{provider.name}".encode()
        ).hexdigest()[:20]
        path = cache / f"{talk['video_id']}-{key}.json"
        if path.is_file():
            data = json.loads(path.read_text())
            return [Candidate.model_validate(c) for c in data["candidates"]], data["drops"]
        found, drops = extract_talk(provider, talk, seed.limits.max_claims_per_talk + 3)
        path.write_text(
            json.dumps({"candidates": [c.model_dump(mode="json") for c in found], "drops": drops})
        )
        return found, drops

    drops_total: dict[str, int] = {}
    candidates: list[Candidate] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for found, drops in pool.map(work, talks):
            candidates.extend(found)
            for reason, count in drops.items():
                drops_total[reason] = drops_total.get(reason, 0) + count
    candidates.sort(key=lambda c: (c.video_id, c.start_seconds))
    out = stage_cache("candidates") / f"{seed.slug}.json"
    out.write_text(json.dumps([c.model_dump(mode="json") for c in candidates], indent=1))
    write_report(
        "extract",
        seed.slug,
        len(talks),
        len(candidates),
        drops_total,
        [f"provider={provider.name} model={provider.model} prompt={PROMPT_VERSION}"],
    )
    return len(candidates)
