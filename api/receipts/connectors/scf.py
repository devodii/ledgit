import re
from typing import ClassVar

from pydantic import BaseModel

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.http import HttpClient

BASE = "https://communityfund.stellar.org"
SUFFIXES = {"labs", "lab", "inc", "ltd", "llc", "foundation", "co", "corp", "limited", "gmbh"}


class ScfProject(BaseModel):
    name: str
    slug: str
    url: str
    awarded_usd: float | None = None


def normalize_name(name: str) -> str:
    words = [w for w in re.sub(r"[^a-z0-9 ]+", " ", name.lower()).split() if w not in SUFFIXES]
    return " ".join(words)


def strip_tags(html: str) -> str:
    html = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def parse_amount(text: str) -> float | None:
    match = re.search(r"Total awarded\s*\$\s*([\d.,]+)\s*([KkMm]?)", text)
    if not match:
        return None
    value = float(match.group(1).replace(",", ""))
    return value * {"": 1, "k": 1_000, "m": 1_000_000}[match.group(2).lower()]


class ScfConnector(Connector):
    name: ClassVar[str] = "scf"
    allowed_domains: ClassVar[list[str]] = ["communityfund.stellar.org"]
    rate_limit_rps: ClassVar[float] = 1.0
    emits: ClassVar[list[str]] = ["ScfProject"]

    def __init__(self) -> None:
        self.http = HttpClient(
            name=self.name,
            allowed_domains=self.allowed_domains,
            rate_limit_rps=self.rate_limit_rps,
            respect_robots=True,
        )
        self._index: dict[str, tuple[str, str]] | None = None

    def index(self) -> dict[str, tuple[str, str]]:
        if self._index is None:
            html = self.http.get(f"{BASE}/projects", cache_ttl=86400).text
            found: dict[str, tuple[str, str]] = {}
            for slug, name in re.findall(
                r'<a href="/project/([^"]+)"><p[^>]*>([^<]+)</p></a>', html
            ):
                found.setdefault(normalize_name(name), (slug, name.strip()))
            self._index = found
        return self._index

    def lookup(self, org_name: str) -> ScfProject | None:
        hit = self.index().get(normalize_name(org_name))
        if hit is None:
            return None
        slug, name = hit
        url = f"{BASE}/project/{slug}"
        page = self.http.get(url, cache_ttl=86400)
        return ScfProject(
            name=name, slug=slug, url=url, awarded_usd=parse_amount(strip_tags(page.text))
        )

    def healthcheck(self) -> HealthResult:
        try:
            index = self.index()
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(connector=self.name, ok=bool(index), detail=f"{len(index)} projects")
