import hashlib
import json
import re

from pydantic import BaseModel, Field, ValidationError

from receipts.llm import LLMError, LLMProvider
from receipts.models.pipeline import Candidate, EvidenceDraft
from receipts.pipeline.common import stage_cache

RELEVANCE_VERSION = "v2"

SYSTEM = """You decide which public references can verify one specific claim made in a conference talk, for a fact-check site. A verdict of "found live" will be shown to the public next to the speaker's words, so linking evidence that does not match what was actually claimed would be a serious error. Be strict.

You get the claim (quote and summary) and numbered candidate references (an asset, a contract, an anchor domain, a protocol or core release).

Select a reference only if BOTH hold:
1. The claim's own words are about that asset, contract, product, or release.
2. What the claim asserts (that it is live, launched, available, deployed, or active) is something that reference can confirm. Past or present tense statements fit. A statement about a future plan, a hypothetical, an integration that merely involves the organisation, or a different product does NOT fit, even if the same organisation owns the reference.

Examples: "PYUSD is live on Stellar" fits the PYUSD asset. "When this goes live they will launch pay with crypto" does not fit PYUSD. "Protocol 23 launched on mainnet" fits protocol 23. "We are working on our next release" does not fit any release. If nothing clearly fits, select nothing.

Reply with JSON only: {"selected":[{"index":0,"reason":"one short sentence quoting the words that match"}]}"""


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
