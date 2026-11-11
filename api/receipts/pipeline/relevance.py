import hashlib
import json
import re

from pydantic import BaseModel, Field, ValidationError

from receipts.llm import LLMError, LLMProvider
from receipts.models.pipeline import Candidate, EvidenceDraft
from receipts.pipeline.common import stage_cache

RELEVANCE_VERSION = "v1"

SYSTEM = """You decide which public references directly relate to one specific claim made in a conference talk, for a fact-check site. Wrongly linking unrelated evidence would make a claim look verified when it is not, so be strict.

You get the claim (quote and summary) and numbered candidate references (an asset, a contract, an anchor domain). Select a reference only if the claim's subject is that reference's asset, contract, product or service, or the reference is clearly the thing the claim says launched, is live, or is coming. Do NOT select references that merely belong to the same organisation but are about something else. If nothing clearly relates, select nothing.

Reply with JSON only: {"selected":[{"index":0,"reason":"one short sentence"}]}"""


class Pick(BaseModel):
    index: int
    reason: str = ""


class Picks(BaseModel):
    selected: list[Pick] = Field(default_factory=list)


def describe(index: int, item: EvidenceDraft) -> str:
    return f"[{index}] {item.kind} {item.ref} (found via: {item.found_via[:200]})"


def select_relevant(
    provider: LLMProvider, candidate: Candidate, items: list[EvidenceDraft], key: str
) -> list[EvidenceDraft]:
    if not items:
        return []
    cache = stage_cache("relevance") / f"{key}-{RELEVANCE_VERSION}.json"
    listing_hash = hashlib.sha256("".join(i.ref for i in items).encode()).hexdigest()[:10]
    if cache.is_file():
        data = json.loads(cache.read_text())
        if data.get("listing") == listing_hash:
            return [EvidenceDraft.model_validate(e) for e in data["selected"]]
    prompt = (
        f"CLAIM QUOTE: {candidate.quote}\nCLAIM SUMMARY: {candidate.summary}\n"
        f"ORGANISATION: {candidate.org_name}\n\nCANDIDATE REFERENCES:\n"
        + "\n".join(describe(i, item) for i, item in enumerate(items))
    )
    picks = Picks()
    for _ in range(2):
        try:
            raw = provider.complete(SYSTEM, prompt)
            cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M)
            start, end = cleaned.find("{"), cleaned.rfind("}")
            picks = Picks.model_validate(json.loads(cleaned[start : end + 1]))
            break
        except (ValueError, ValidationError, LLMError):
            continue
    selected: list[EvidenceDraft] = []
    for pick in picks.selected:
        if 0 <= pick.index < len(items):
            item = items[pick.index].model_copy()
            item.found_via = f"{item.found_via} | relevance: {pick.reason}"
            selected.append(item)
    cache.write_text(
        json.dumps({"listing": listing_hash, "selected": [e.model_dump() for e in selected]})
    )
    return selected
