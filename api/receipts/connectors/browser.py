from typing import ClassVar

from playwright.sync_api import sync_playwright

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.errors import HumanActionRequired
from receipts.settings import get_settings

BOT_WALL_MARKERS = (
    "just a moment",
    "verify you are human",
    "are you a robot",
    "captcha",
    "cf-challenge",
    "access denied",
    "please log in",
    "sign in to continue",
)


def detect_wall(html: str) -> str | None:
    lowered = html.lower()
    for marker in BOT_WALL_MARKERS:
        if marker in lowered:
            return marker
    return None


class BrowserConnector(Connector):
    name: ClassVar[str] = "browser"
    allowed_domains: ClassVar[list[str]] = ["*"]
    rate_limit_rps: ClassVar[float] = 0.5
    emits: ClassVar[list[str]] = ["RenderedPage"]

    def render(self, url: str) -> str:
        settings = get_settings()
        settings.browser_profile_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                str(settings.browser_profile_dir), headless=not settings.browser_headful
            )
            try:
                page = context.new_page()
                page.set_default_timeout(settings.browser_timeout_ms)
                page.goto(url, wait_until="networkidle")
                html = page.content()
            finally:
                context.close()
        wall = detect_wall(html)
        if wall:
            raise HumanActionRequired(
                kind="bot_wall",
                description=f"{url} showed a bot or login wall ({wall}).",
                url=url,
                resume_hint="Run with BROWSER_HEADFUL=1, solve it in the window, rerun the stage.",
            )
        return html

    def healthcheck(self) -> HealthResult:
        try:
            html = self.render("https://example.com")
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(connector=self.name, ok="Example Domain" in html, detail="rendered")
