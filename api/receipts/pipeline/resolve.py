import json
import re
from datetime import UTC, datetime
from urllib.parse import urlparse

from receipts.connectors.errors import ConnectorError
from receipts.connectors.horizon import HorizonConnector
from receipts.connectors.lumenloop import LumenLoopConnector
from receipts.connectors.scf import ScfConnector, normalize_name
from receipts.connectors.stellar_expert import StellarExpertConnector
from receipts.connectors.stellarlight import StellarLightConnector
from receipts.llm import LLMProvider, get_provider
from receipts.models.enums import ClaimType
from receipts.models.pipeline import (
    Candidate,
    EvidenceDraft,
    OrgResolution,
    SourceDraft,
)
from receipts.models.registry import EventSeed, OrgRef
from receipts.pipeline.common import stage_cache, write_report
from receipts.pipeline.domain import fetch_toml, host_of, propose_domain, verify_domain
from receipts.pipeline.relevance import select_relevant

CONTRACT_RE = re.compile(r"^C[A-Z2-7]{55}$")
ACCOUNT_RE = re.compile(r"^G[A-Z2-7]{55}$")


def valid_ref(kind: str, ref: str) -> bool:
    if kind == "soroban_contract":
        return bool(CONTRACT_RE.match(ref))
    if kind == "asset_issuer":
        issuer = ref.rpartition("-")[2]
        return bool(ACCOUNT_RE.match(issuer))
    return True


def clean_domain(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return ""
    host = urlparse(value if "//" in value else f"//{value}").hostname or ""
    return host.removeprefix("www.")


def now() -> datetime:
    return datetime.now(UTC)


def resolve_org(name: str, hint_domain: str, quote: str, provider: LLMProvider) -> OrgResolution:
    slug = OrgRef(name=name).slug
    result = OrgResolution(org_name=name, slug=slug)
    sources: dict[str, SourceDraft] = {}
    evidence: dict[tuple[str, str, str], EvidenceDraft] = {}

    def source(name_: str, url: str, provides: str) -> str:
        key = f"{name_}|{url}"
        if key not in sources:
            sources[key] = SourceDraft(name=name_, url=url, retrieved_at=now(), provides=[])
        if provides not in sources[key].provides:
            sources[key].provides.append(provides)
        return f"{name_} {url}"

    def add_evidence(kind: str, ref: str, via: str, network: str = "pubnet") -> None:
        if valid_ref(kind, ref):
            evidence.setdefault(
                (kind, network, ref),
                EvidenceDraft(kind=kind, network=network, ref=ref, found_via=via),
            )

    target = normalize_name(name)
    light = StellarLightConnector()
    lumen = LumenLoopConnector()

    # candidate domains, each with where it came from
    candidates: list[tuple[str, str]] = []
    if hint_domain:
        candidates.append((host_of(hint_domain), "spoken or written in the talk"))
    light_hits = []
    try:
        light_hits = [
            p for p in light.search_projects(name, limit=10) if normalize_name(p.name) == target
        ]
    except ConnectorError:
        pass
    for project in light_hits:
        if project.website:
            candidates.append(
                (
                    host_of(project.website),
                    source(
                        "stellarlight",
                        f"https://stellarlight.xyz/project/{project.slug}",
                        "website",
                    ),
                )
            )
    lumen_hit = None
    try:
        matches = [
            p for p in lumen.search_directory(name, limit=10) if normalize_name(p.title) == target
        ]
        if matches:
            lumen_hit = lumen.project(matches[0].slug) or matches[0]
            url = f"https://lumenloop.com/directory/{matches[0].slug}"
            if lumen_hit.website:
                candidates.append((host_of(lumen_hit.website), source("lumenloop", url, "website")))
            region = lumen_hit.based_in or lumen_hit.operating_region
            if region:
                result.country = region
                result.country_source = source("lumenloop", url, "region")
    except ConnectorError:
        pass

    domain, domain_source, toml = "", "", None
    seen: set[str] = set()
    for candidate, origin in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        candidate_toml = fetch_toml(candidate)
        domain, domain_source, toml = candidate, origin, candidate_toml
        break
    if not domain:
        proposed = propose_domain(provider, name, quote)
        if proposed:
            proposed_toml = fetch_toml(proposed)
            ok, how = verify_domain(name, proposed, proposed_toml)
            if ok:
                domain, toml = proposed, proposed_toml
                domain_source = f"proposed by the extraction model, verified: {how}"
                source(
                    "stellar_toml" if "stellar.toml" in how else "homepage",
                    how.split("(")[-1].rstrip(")"),
                    "domain verification",
                )

    if domain and toml:
        result.domain, result.domain_source = domain, domain_source
        if toml.reachable:
            via = f"stellar_toml {toml.url}"
            source("stellar_toml", toml.url, "accounts, currencies, sep endpoints")
            if toml.endpoints:
                add_evidence("anchor", domain, via)
            for currency in toml.currencies:
                if currency.code and ACCOUNT_RE.match(currency.issuer):
                    add_evidence("asset_issuer", f"{currency.code}-{currency.issuer}", via)
                if CONTRACT_RE.match(currency.contract):
                    add_evidence("soroban_contract", currency.contract, via)

        # every StellarLight project hosted on this domain
        keyword = domain.split(".")[0]
        try:
            for project in light.search_projects(keyword, limit=25):
                if host_of(project.website) != domain and normalize_name(project.name) != target:
                    continue
                url = f"https://stellarlight.xyz/project/{project.slug}"
                via = f"stellarlight project {project.slug}: {project.status_source_url or url}"
                for contract in project.contracts:
                    add_evidence("soroban_contract", contract.address, via)
                    source("stellarlight", project.status_source_url or url, "contract")
                if project.asset_code and project.asset_issuer:
                    add_evidence(
                        "asset_issuer", f"{project.asset_code}-{project.asset_issuer}", via
                    )
                    source("stellarlight", url, "asset")
                if not result.scf_found and project.scf_awarded and project.scf_source_url:
                    result.scf_found = True
                    result.scf_project_url = project.scf_source_url
                    result.scf_awarded_usd = project.scf_total_usd
                    result.scf_source = source("stellarlight", project.scf_source_url, "scf award")
        except ConnectorError:
            pass

        try:
            expert_url = "https://api.stellar.expert/explorer/directory"
            horizon = HorizonConnector()
            for entry in StellarExpertConnector().search_directory(domain, limit=10):
                if host_of(entry.domain) != domain:
                    continue
                via = f"stellar_expert directory {expert_url}?search={domain}"
                if CONTRACT_RE.match(entry.address):
                    add_evidence("soroban_contract", entry.address, via)
                    source("stellar_expert", expert_url, "directory address")
                elif ACCOUNT_RE.match(entry.address):
                    for asset in horizon.issued_assets(entry.address):
                        add_evidence("asset_issuer", f"{asset.code}-{entry.address}", via)
                        source("stellar_expert", expert_url, "directory address")
        except ConnectorError:
            pass

    try:
        scf = ScfConnector().lookup(name)
    except ConnectorError:
        scf = None
    if scf and not result.scf_found:
        result.scf_found = True
        result.scf_project_url = scf.url
        result.scf_awarded_usd = scf.awarded_usd
        result.scf_source = source("scf", scf.url, "scf award")

    result.evidence = sorted(evidence.values(), key=lambda e: (e.kind, e.network, e.ref))
    result.sources = sorted(sources.values(), key=lambda s: (s.name, s.url))
    return result


TICKER_RE = re.compile(r"\b[A-Z][A-Z0-9]{2,7}\b")
NOT_TICKERS = {
    "SDF", "SEC", "USD", "API", "SDK", "RPC", "CAP", "SEP", "DAO", "NFT", "AMM", "DEX", "EVM",
    "RWA", "CEO", "CTO", "CFO", "AI", "UX", "KYC", "AML", "ZK", "SCF", "FAQ", "URL", "JSON",
}  # fmt: skip


def resolve_claim_extras(candidate: Candidate, org_domain: str) -> OrgResolution:
    """Evidence tied to this specific claim: asset tickers and versions named in the talk."""
    result = OrgResolution(org_name=candidate.org_name, slug=claim_key(candidate))
    light = StellarLightConnector()
    horizon = HorizonConnector()
    seen: set[str] = set()
    sources: dict[str, SourceDraft] = {}
    claim_text = f"{candidate.quote} {candidate.summary}"
    tickers = [
        t
        for t in dict.fromkeys(
            [
                c
                for c in candidate.asset_codes
                if re.search(rf"\b{re.escape(c)}\b", claim_text, re.I)
            ]
            + TICKER_RE.findall(claim_text)
        )
        if t not in NOT_TICKERS
    ]

    def add(kind: str, ref: str, via: str, origin: str, name: str, provides: str) -> None:
        if valid_ref(kind, ref) and not any(e.ref == ref for e in result.evidence):
            result.evidence.append(EvidenceDraft(kind=kind, ref=ref, found_via=via))
            sources[origin] = SourceDraft(
                name=name, url=origin, retrieved_at=now(), provides=[provides]
            )

    for ticker in tickers:
        if ticker in seen:
            continue
        seen.add(ticker)
        try:
            hits = [p for p in light.search_projects(ticker, limit=10) if p.name.upper() == ticker]
        except ConnectorError:
            hits = []
        for project in hits:
            url = f"https://stellarlight.xyz/project/{project.slug}"
            via = f"ticker {ticker} named in the claim; stellarlight project {project.slug}: {url}"
            pointers = [(ref.kind, ref.ref, ref.source_url) for ref in project.refs]
            if project.asset_code and valid_ref("asset_issuer", f"x-{project.asset_issuer}"):
                pointers.append(
                    ("asset_issuer", f"{project.asset_code}-{project.asset_issuer}", url)
                )
            for kind, ref, origin in pointers:
                add(
                    kind,
                    ref,
                    f"{via} (pointer: {origin})",
                    origin,
                    "stellarlight",
                    f"asset {ticker}",
                )
        if org_domain and len(ticker) >= 3:
            try:
                issuers = horizon.assets_by_code(ticker)
                if 0 < len(issuers) <= 60:
                    for asset in issuers:
                        if host_of(horizon.home_domain(asset.issuer)) == org_domain:
                            origin = f"https://horizon.stellar.lobstr.co/assets?asset_code={ticker}"
                            add(
                                "asset_issuer",
                                f"{ticker}-{asset.issuer}",
                                f"ticker {ticker} named in the claim; issuer account home_domain is {org_domain} (horizon {origin})",
                                origin,
                                "horizon",
                                f"issuer of {ticker}",
                            )
            except ConnectorError:
                pass
    if candidate.core_version:
        add(
            "protocol_upgrade",
            f"core-{candidate.core_version}",
            f"core version {candidate.core_version} named in the talk",
            f"https://www.youtube.com/watch?v={candidate.video_id}&t={candidate.start_seconds}s",
            "talk",
            "core version",
        )
    if candidate.protocol_version:
        add(
            "protocol_upgrade",
            f"protocol-{candidate.protocol_version}",
            f"protocol {candidate.protocol_version} named in the talk",
            f"https://www.youtube.com/watch?v={candidate.video_id}&t={candidate.start_seconds}s",
            "talk",
            "protocol version",
        )
    result.sources = list(sources.values())
    return result


def claim_key(candidate: Candidate) -> str:
    import hashlib

    return hashlib.sha256(f"{candidate.video_id}|{candidate.quote}".encode()).hexdigest()[:12]


def run_resolve(seed: EventSeed) -> int:
    judged = [
        Candidate.model_validate(c)
        for c in json.loads((stage_cache("judged") / f"{seed.slug}.json").read_text())
    ]
    cache = stage_cache("resolve")
    claims_cache = stage_cache("resolve-claims")
    provider = get_provider()
    resolved = 0
    drops: dict[str, int] = {}
    for candidate in judged:
        slug = OrgRef(name=candidate.org_name).slug
        path = cache / f"{slug}.json"
        if path.is_file():
            resolution = OrgResolution.model_validate_json(path.read_text())
        else:
            resolution = resolve_org(
                candidate.org_name, candidate.org_domain, candidate.quote, provider
            )
            path.write_text(resolution.model_dump_json(indent=1))
            resolved += 1
        extras_path = claims_cache / f"{claim_key(candidate)}.json"
        if not extras_path.is_file():
            extras = resolve_claim_extras(candidate, resolution.domain)
            org_level = (
                []
                if candidate.claim_type == ClaimType.protocol_feature
                else list(resolution.evidence)
            )
            pool = extras.evidence + org_level
            chosen = select_relevant(provider, candidate, pool, claim_key(candidate))
            extras.evidence = chosen
            extras_path.write_text(extras.model_dump_json(indent=1))
        if not json.loads(extras_path.read_text())["evidence"]:
            drops["no_relevant_evidence"] = drops.get("no_relevant_evidence", 0) + 1
    write_report(
        "resolve",
        seed.slug,
        len(judged),
        len(judged) - drops.get("no_relevant_evidence", 0),
        drops,
        [f"new organisations resolved: {resolved}", "counts_out is claims with evidence"],
    )
    return resolved
