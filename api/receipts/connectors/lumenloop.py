import json
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.errors import ConnectorError
from receipts.connectors.http import HttpClient

ENDPOINT = "https://mcp.lumenloop.com"


class LumenLoopProject(BaseModel):
    slug: str
    title: str
    category: str = ""
    website: str = ""
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    based_in: str = ""
    operating_region: str = ""


class LumenLoopConnector(Connector):
    name: ClassVar[str] = "lumenloop"
    allowed_domains: ClassVar[list[str]] = ["mcp.lumenloop.com", "lumenloop.com"]
    rate_limit_rps: ClassVar[float] = 2.0
    emits: ClassVar[list[str]] = ["LumenLoopProject", "ScfSubmissions", "AvPassages"]

    def __init__(self) -> None:
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )
        self._session: str | None = None

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())  # type: ignore[no-any-return]
        return json.loads(raw)  # type: ignore[no-any-return]

    def _rpc(self, method: str, params: dict[str, Any] | None = None, *, rid: int = 2) -> Any:
        headers = {"accept": "application/json, text/event-stream"}
        if self._session:
            headers["mcp-session-id"] = self._session
        response = self.http.post(
            ENDPOINT,
            json_body={"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}},
            headers=headers,
            cache_ttl=86400 if method == "tools/call" else None,
        )
        body = self._parse(response.text)
        if "error" in body:
            raise ConnectorError(f"lumenloop {method}: {body['error']}")
        return body["result"]

    def _ensure_session(self) -> None:
        if self._session:
            return
        raw = self.http._client.post(
            ENDPOINT,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "ledgit", "version": "0.1"},
                },
            },
            headers={"accept": "application/json, text/event-stream"},
        )
        session = raw.headers.get("mcp-session-id")
        if not session:
            raise ConnectorError("lumenloop did not return a session id")
        self._session = session
        self.http._client.post(
            ENDPOINT,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers={"accept": "application/json, text/event-stream", "mcp-session-id": session},
        )

    def call(self, tool: str, arguments: dict[str, Any]) -> Any:
        self._ensure_session()
        result = self._rpc("tools/call", {"name": tool, "arguments": arguments})
        if result.get("isError"):
            raise ConnectorError(f"lumenloop {tool} failed: {result['content'][0]['text'][:200]}")
        text = result["content"][0]["text"]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    def search_directory(self, query: str, limit: int = 10) -> list[LumenLoopProject]:
        data = self.call("search_directory", {"query": query, "limit": limit})
        return [self._project(p) for p in data.get("projects", [])]

    @staticmethod
    def _project(raw: dict[str, Any]) -> LumenLoopProject:
        website = raw.get("website") or ""
        if website.startswith("["):
            try:
                website = (json.loads(website) or [""])[0]
            except json.JSONDecodeError:
                website = ""
        return LumenLoopProject(
            slug=raw["slug"],
            title=raw.get("title", ""),
            category=raw.get("category") or "",
            website=website,
            description=raw.get("description") or "",
            tags=raw.get("tags") or [],
            based_in=raw.get("based_in") or "",
            operating_region=raw.get("operating_region") or "",
        )

    def project(self, slug: str) -> LumenLoopProject | None:
        data = self.call("get_project", {"slug": slug})
        if not isinstance(data, dict):
            return None
        row = data.get("project", data)
        return self._project({**row, "slug": row.get("slug", slug)}) if row else None

    def scf_submissions(self, slug: str) -> Any:
        return self.call("get_scf_submissions", {"slug": slug})

    def av_passages(self, query: str, limit: int = 10) -> Any:
        return self.call("find_av_passages", {"query": query, "limit": limit})

    def healthcheck(self) -> HealthResult:
        try:
            projects = self.search_directory("Blend", limit=2)
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(
            connector=self.name, ok=bool(projects), detail=f"{len(projects)} projects"
        )
