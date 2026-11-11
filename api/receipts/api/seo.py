import html
import textwrap
from io import BytesIO
from typing import Annotated
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from PIL import Image, ImageDraw, ImageFont

from receipts.api.queries import STATUS_EXPR
from receipts.db.connection import Conn, get_conn
from receipts.settings import get_settings

router = APIRouter(tags=["seo"])

STATUS_LABEL = {
    "live": "Found live on Stellar mainnet",
    "testnet_only": "Found on testnet, not yet on mainnet",
    "no_trace_found": "We found no on-chain trace yet",
    "pending": "Too recent to assess",
    "open_ask": "Requested on stage, no builder identified",
}
STATUS_COLOR = {
    "live": (94, 234, 212),
    "testnet_only": (251, 191, 36),
    "no_trace_found": (180, 188, 205),
    "pending": (196, 181, 253),
    "open_ask": (125, 211, 252),
}


def _claim(conn: Conn, claim_id: str) -> dict[str, object]:
    row = conn.execute(
        f"""
        SELECT c.id, c.quote, c.summary, c.speaker_name, o.name AS org_name,
               {STATUS_EXPR} AS status
        FROM claims c JOIN orgs o ON o.slug = c.org_slug
        LEFT JOIN verdicts v ON v.claim_id = c.id WHERE c.id = %s
        """,
        (claim_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="claim not found")
    return dict(row)


@router.get("/api/v1/claims/{claim_id}/og.png", include_in_schema=False)
def share_image(claim_id: str, conn: Annotated[Conn, Depends(get_conn)]) -> Response:
    claim = _claim(conn, claim_id)
    status = str(claim["status"])
    image = Image.new("RGB", (1200, 630), (11, 13, 18))
    draw = ImageDraw.Draw(image)
    color = STATUS_COLOR[status]
    draw.rectangle((0, 0, 14, 630), fill=color)
    draw.text((64, 54), "Ledgit", fill=(232, 235, 242), font=ImageFont.load_default(36))
    draw.text(
        (64, 120), str(claim["org_name"]), fill=(232, 235, 242), font=ImageFont.load_default(54)
    )
    quote = textwrap.fill(f"“{claim['quote']}”", width=52)
    lines = quote.splitlines()[:6]
    draw.multiline_text(
        (64, 210),
        "\n".join(lines),
        fill=(163, 171, 189),
        font=ImageFont.load_default(34),
        spacing=10,
    )
    draw.rounded_rectangle(
        (64, 520, 64 + 24 + 17 * len(STATUS_LABEL[status]), 580), 30, outline=color, width=3
    )
    draw.text((88, 534), STATUS_LABEL[status], fill=color, font=ImageFont.load_default(28))
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return Response(
        buffer.getvalue(), media_type="image/png", headers={"cache-control": "public, max-age=3600"}
    )


@router.get("/share/claims/{claim_id}", include_in_schema=False)
def share_page(claim_id: str, conn: Annotated[Conn, Depends(get_conn)]) -> HTMLResponse:
    claim = _claim(conn, claim_id)
    site = get_settings().site_url.rstrip("/")
    title = f"{claim['org_name']}: {STATUS_LABEL[str(claim['status'])]}"
    description = html.escape(str(claim["summary"]))
    target = f"{site}/claims/{claim_id}"
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="description" content="{description}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Ledgit">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{target}">
<meta property="og:image" content="{site}/api/v1/claims/{claim_id}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
</head><body><a href="{target}">{html.escape(title)}</a></body></html>"""
    return HTMLResponse(page)


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap(conn: Annotated[Conn, Depends(get_conn)]) -> Response:
    site = get_settings().site_url.rstrip("/")
    urls = [f"{site}/", f"{site}/open-asks", f"{site}/changes", f"{site}/methodology"]
    urls += [
        f"{site}/claims/{r['id']}"
        for r in conn.execute("SELECT id FROM claims ORDER BY id").fetchall()
    ]
    urls += [
        f"{site}/orgs/{r['slug']}"
        for r in conn.execute("SELECT slug FROM orgs ORDER BY slug").fetchall()
    ]
    body = "".join(f"<url><loc>{escape(u)}</loc></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'
    return Response(xml, media_type="application/xml")


@router.get("/robots.txt", include_in_schema=False)
def robots() -> Response:
    site = get_settings().site_url.rstrip("/")
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {site}/sitemap.xml\n", media_type="text/plain"
    )
