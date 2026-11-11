import json
import re
from datetime import UTC, datetime
from urllib.parse import urlparse

from receipts.connectors.errors import ConnectorError
from receipts.connectors.horizon import HorizonConnector
from receipts.connectors.lumenloop import LumenLoopConnector
from receipts.connectors.scf import ScfConnector, normalize_name
from receipts.connectors.stellar_expert import StellarExpertConnector
from receipts.connectors.stellar_toml import StellarTomlConnector
from receipts.connectors.stellarlight import StellarLightConnector
from receipts.models.pipeline import (
    Candidate,
    EvidenceDraft,
    OrgResolution,
    SourceDraft,
)
from receipts.models.registry import EventSeed, OrgRef
from receipts.pipeline.common import stage_cache, write_report

CONTRACT_RE = re.compile(r"^C[A-Z2-7]{55}$")
ACCOUNT_RE = re.compile(r"^G[A-Z2-7]{55}$")


def clean_domain(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return ""
    host = urlparse(value if "//" in value else f"//{value}").hostname or ""
    return host.removeprefix("www.")


def now() -> datetime:
    return datetime.now(UTC)


def resolve_org(name: str, hint_domain: str) -> OrgResolution:
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
        return url

    def add_evidence(kind: str, ref: str, via: str, network: str = "pubnet") -> None:
        evidence.setdefault(
            (kind, network, ref), EvidenceDraft(kind=kind, network=network, ref=ref, found_via=via)
        )

    target = normalize_name(name)

    try:
        scf = ScfConnector().lookup(name)
    except ConnectorError:
        scf = None
    if scf:
        result.scf_found = True
        result.scf_project_url = scf.url
        result.scf_awarded_usd = scf.awarded_usd
        result.scf_source = source("scf", scf.url, "scf award")

    domain, domain_source = clean_domain(hint_domain), ""
    if domain:
        domain_source = "spoken or written in the talk"

    try:
        lumen = LumenLoopConnector()
        matches = [
            p for p in lumen.search_directory(name, limit=10) if normalize_name(p.title) == target
        ]
        if matches:
            detail = lumen.project(matches[0].slug) or matches[0]
            url = f"https://lumenloop.com/directory/{matches[0].slug}"
            if not domain and detail.website:
                domain = clean_domain(detail.website)
                domain_source = source("lumenloop", url, "website")
            region = detail.based_in or detail.operating_region
            if region:
                result.country = region
                result.country_source = source("lumenloop", url, "region")
    except ConnectorError:
        pass

    try:
        light = StellarLightConnector()
        hits = [
            p for p in light.search_projects(name, limit=10) if normalize_name(p.name) == target
        ]
        if hits:
            project = hits[0]
            url = f"https://stellarlight.xyz/api/projects/search?q={name}"
            for contract in project.contracts:
                add_evidence(
                    "soroban_contract",
                    contract.address,
                    f"stellarlight project {project.slug}: {project.status_source_url or url}",
                )
                source("stellarlight", project.status_source_url or url, "contract")
            if project.asset_code and project.asset_issuer:
                add_evidence(
                    "asset_issuer",
                    f"{project.asset_code}-{project.asset_issuer}",
                    f"stellarlight project {project.slug}: {url}",
                )
                source("stellarlight", url, "asset")
            if not result.scf_found and project.scf_awarded and project.scf_source_url:
                result.scf_found = True
                result.scf_project_url = project.scf_source_url
                result.scf_awarded_usd = project.scf_total_usd
                result.scf_source = source("stellarlight", project.scf_source_url, "scf award")
    except ConnectorError:
        pass

    if domain:
        toml = StellarTomlConnector().fetch(domain)
        if toml.reachable:
            result.domain, result.domain_source = domain, domain_source
            via = f"stellar_toml {toml.url}"
            source("stellar_toml", toml.url, "accounts, currencies, sep endpoints")
            if toml.endpoints:
                add_evidence("anchor", domain, via)
            for currency in toml.currencies:
                if currency.code and ACCOUNT_RE.match(currency.issuer):
                    add_evidence("asset_issuer", f"{currency.code}-{currency.issuer}", via)
                if CONTRACT_RE.match(currency.contract):
                    add_evidence("soroban_contract", currency.contract, via)
        else:
            result.domain, result.domain_source = domain, f"{domain_source} (no stellar.toml found)"

    if result.domain:
        try:
            expert_url = "https://api.stellar.expert/explorer/directory"
            horizon = HorizonConnector()
            for entry in StellarExpertConnector().search_directory(result.domain, limit=10):
                if clean_domain(entry.domain) != result.domain:
                    continue
                via = f"stellar_expert directory {expert_url}?search={result.domain}"
                if CONTRACT_RE.match(entry.address):
                    add_evidence("soroban_contract", entry.address, via)
                    source("stellar_expert", expert_url, "directory address")
                elif ACCOUNT_RE.match(entry.address) and horizon.issued_assets(entry.address):
                    add_evidence("asset_issuer", entry.address, via)
                    source("stellar_expert", expert_url, "directory address")
        except ConnectorError:
            pass

    result.evidence = sorted(evidence.values(), key=lambda e: (e.kind, e.network, e.ref))
    result.sources = sorted(sources.values(), key=lambda s: (s.name, s.url))
    return result


def run_resolve(seed: EventSeed) -> int:
    ranked = [
        Candidate.model_validate(c)
        for c in json.loads((stage_cache("ranked") / f"{seed.slug}.json").read_text())
    ]
    cache = stage_cache("resolve")
    resolved = 0
    drops: dict[str, int] = {}
    for candidate in ranked:
        slug = OrgRef(name=candidate.org_name).slug
        path = cache / f"{slug}.json"
        if path.is_file():
            continue
        resolution = resolve_org(candidate.org_name, candidate.org_domain)
        path.write_text(resolution.model_dump_json(indent=1))
        resolved += 1
        if not resolution.evidence:
            drops["no_evidence_found"] = drops.get("no_evidence_found", 0) + 1
    write_report(
        "resolve", seed.slug, len(ranked), resolved, drops, ["counts are new orgs resolved"]
    )
    return resolved
