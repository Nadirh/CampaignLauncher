import ipaddress
import logging
import socket
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error as PlaywrightError

from app.schemas.pipeline import PageContent

logger = logging.getLogger(__name__)

FETCH_TIMEOUT = 30000  # milliseconds for Playwright
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB


class PageFetchError(Exception):
    pass


def validate_url(url: str) -> str:
    """Validate URL scheme and block private/reserved IPs (SSRF protection)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise PageFetchError(f"Invalid URL scheme: {parsed.scheme}")
    if not parsed.hostname:
        raise PageFetchError("URL has no hostname")

    try:
        resolved = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        raise PageFetchError(f"Cannot resolve hostname: {parsed.hostname}")

    for _, _, _, _, addr in resolved:
        ip = ipaddress.ip_address(addr[0])
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            raise PageFetchError("URL resolves to a private or reserved IP address")

    return url


def _parse_content(html: str, url: str) -> PageContent:
    """Extract structured content from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        title = title_tag.string.strip()

    meta_description = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_description = str(meta_tag["content"]).strip()

    headings: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text:
            headings.append(text)

    hero_text = ""
    hero = soup.find(["section", "div"], class_=lambda c: c and "hero" in str(c).lower())
    if hero:
        hero_text = hero.get_text(separator=" ", strip=True)

    ctas: list[str] = []
    for a_tag in soup.find_all("a", class_=lambda c: c and any(
        k in str(c).lower() for k in ("cta", "btn", "button")
    )):
        text = a_tag.get_text(strip=True)
        if text:
            ctas.append(text)
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        if text and text not in ctas:
            ctas.append(text)

    features: list[str] = []
    for ul in soup.find_all("ul"):
        parent_heading = ul.find_previous_sibling(["h2", "h3"])
        if parent_heading and "feature" in parent_heading.get_text().lower():
            for li in ul.find_all("li"):
                text = li.get_text(strip=True)
                if text:
                    features.append(text)

    body = soup.find("body")
    raw_text = body.get_text(separator=" ", strip=True) if body else soup.get_text(separator=" ", strip=True)
    raw_text = raw_text[:10000]

    return PageContent(
        url=url,
        title=title,
        meta_description=meta_description,
        headings=headings,
        hero_text=hero_text,
        ctas=ctas,
        features=features,
        raw_text=raw_text,
    )


async def _fetch_with_playwright(url: str) -> str:
    """Fetch page HTML using Playwright headless Chromium (renders JavaScript)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(
                user_agent="CampaignLauncher/1.0",
            )
            response = await page.goto(url, wait_until="networkidle", timeout=FETCH_TIMEOUT)
            if response and response.status >= 400:
                raise PageFetchError(f"HTTP {response.status} fetching {url}")
            html = await page.content()
            return html
        finally:
            await browser.close()


async def fetch_page(url: str) -> PageContent:
    """Fetch a URL with headless browser and return structured page content."""
    validated_url = validate_url(url)

    start = time.monotonic()
    logger.info("Fetching page with Playwright", extra={"url": validated_url})

    try:
        html = await _fetch_with_playwright(validated_url)
    except PageFetchError:
        raise
    except PlaywrightError as exc:
        latency = time.monotonic() - start
        logger.error(
            "Playwright fetch error",
            extra={"url": validated_url, "error": str(exc), "latency_ms": int(latency * 1000)},
        )
        raise PageFetchError(f"Browser fetch failed: {exc}")
    except Exception as exc:
        latency = time.monotonic() - start
        logger.error(
            "Unexpected fetch error",
            extra={"url": validated_url, "error": str(exc), "latency_ms": int(latency * 1000)},
        )
        raise PageFetchError(f"Request failed: {exc}")

    latency = time.monotonic() - start
    logger.info(
        "Page fetched",
        extra={"url": validated_url, "latency_ms": int(latency * 1000)},
    )

    content = _parse_content(html, validated_url)
    return content
