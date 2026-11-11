import hashlib
import json
import re
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel

from receipts.connectors.errors import ConnectorError
from receipts.connectors.http import HttpClient
from receipts.connectors.scf import normalize_name
from receipts.connectors.stellar_toml import StellarToml, StellarTomlConnector
from receipts.llm import LLMError, LLMProvider
from receipts.pipeline.common import stage_cache

DOMAIN_SYSTEM = """You help a fact-check site link organisations named in Stellar conference talks to their official website.
Given an organisation name and a quote from the talk, reply with JSON only: {"domain": "example.com"} using the registrable domain of the organisation's own official website (no scheme, no path, no www). If you are not confident, reply {"domain": ""}. Never guess."""


class DomainProposal(BaseModel):
    domain: str = ""


def registrable(host: str) -> str:
    host = (host or "").lower().removeprefix("www.")
    parts = host.split(".")
    if len(parts) > 2 and parts[-2] in {"co", "com", "org", "gov", "ac"} and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def host_of(url_or_domain: str) -> str:
    value = url_or_domain.strip()
    if not value:
        return ""
    return registrable(urlparse(value if "//" in value else f"//{value}").hostname or "")


def propose_domain(provider: LLMProvider, org: str, quote: str) -> str:
    cache = stage_cache("resolve-llm")
    key = hashlib.sha256(f"{org}|{provider.name}|v1".encode()).hexdigest()[:16]
    path = cache / f"{key}.json"
    if path.is_file():
        return str(json.loads(path.read_text())["domain"])
    domain = ""
    for _ in range(2):
        try:
            raw = provider.complete(DOMAIN_SYSTEM, f"Organisation: {org}\nQuote: {quote}")
            start, end = raw.find("{"), raw.rfind("}")
            domain = host_of(DomainProposal.model_validate(json.loads(raw[start : end + 1])).domain)
            break
        except (ValueError, LLMError):
            continue
    path.write_text(json.dumps({"org": org, "domain": domain}))
    return domain


def name_matches(org: str, texts: list[str]) -> bool:
    target = normalize_name(org)
    if len(target) < 3:
        return False
    return any(target in normalize_name(t) for t in texts if t)


def verify_domain(org: str, domain: str, toml: StellarToml) -> tuple[bool, str]:
    if toml.reachable and name_matches(org, toml.org_names + [toml.org_url]):
        return True, f"stellar.toml DOCUMENTATION names the organisation ({toml.url})"
    client = HttpClient(name="homepage", allowed_domains=[domain], rate_limit_rps=1)
    url = f"https://{domain}/"
    try:
        page = client.get(url, cache_ttl=86400, retries=2)
    except ConnectorError:
        return False, ""
    if page.status != 200:
        return False, ""
    title = re.search(r"<title[^>]*>(.*?)</title>", page.text, re.S | re.I)
    metas = re.findall(
        r'<meta[^>]+(?:property|name)=["\'](?:og:site_name|og:title|application-name)["\'][^>]+content=["\']([^"\']+)',
        page.text,
        re.I,
    )
    texts = ([title.group(1)] if title else []) + metas
    if name_matches(org, texts):
        return True, f"homepage title names the organisation ({url})"
    return False, ""


def fetch_toml(domain: str) -> StellarToml:
    return StellarTomlConnector().fetch(domain)


def site_hosts(values: list[Any]) -> set[str]:
    return {host_of(str(v)) for v in values if v}
