from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.page_fetcher import (
    PageFetchError,
    _parse_content,
    fetch_page,
    validate_url,
)


SAMPLE_HTML = """
<html>
<head>
    <title>Best Project Management Tool</title>
    <meta name="description" content="Manage projects with ease.">
</head>
<body>
    <div class="hero-section">
        <h1>Ship Projects Faster</h1>
        <p>The all-in-one tool for modern teams.</p>
        <a href="/signup" class="cta-button">Get Started Free</a>
    </div>
    <h2>Features</h2>
    <ul>
        <li>Real-time collaboration</li>
        <li>Automated workflows</li>
    </ul>
    <h3>Pricing</h3>
    <button>Start Free Trial</button>
</body>
</html>
"""


class TestValidateUrl:
    def test_valid_https_url(self) -> None:
        with patch("app.services.page_fetcher.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("93.184.216.34", 0))]
            result = validate_url("https://example.com")
            assert result == "https://example.com"

    def test_rejects_ftp_scheme(self) -> None:
        with pytest.raises(PageFetchError, match="Invalid URL scheme"):
            validate_url("ftp://example.com")

    def test_rejects_javascript_scheme(self) -> None:
        with pytest.raises(PageFetchError, match="Invalid URL scheme"):
            validate_url("javascript:alert(1)")

    def test_rejects_no_hostname(self) -> None:
        with pytest.raises(PageFetchError, match="no hostname"):
            validate_url("https://")

    def test_rejects_private_ip(self) -> None:
        with patch("app.services.page_fetcher.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("192.168.1.1", 0))]
            with pytest.raises(PageFetchError, match="private or reserved"):
                validate_url("https://internal.example.com")

    def test_rejects_loopback(self) -> None:
        with patch("app.services.page_fetcher.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("127.0.0.1", 0))]
            with pytest.raises(PageFetchError, match="private or reserved"):
                validate_url("https://localhost")

    def test_rejects_unresolvable_host(self) -> None:
        with patch("app.services.page_fetcher.socket.getaddrinfo") as mock_dns:
            import socket
            mock_dns.side_effect = socket.gaierror("Name or service not known")
            with pytest.raises(PageFetchError, match="Cannot resolve"):
                validate_url("https://nonexistent.invalid")


class TestParseContent:
    def test_extracts_title(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert content.title == "Best Project Management Tool"

    def test_extracts_meta_description(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert content.meta_description == "Manage projects with ease."

    def test_extracts_headings(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert "Ship Projects Faster" in content.headings
        assert "Pricing" in content.headings

    def test_extracts_hero_text(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert "Ship Projects Faster" in content.hero_text

    def test_extracts_ctas(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert "Get Started Free" in content.ctas
        assert "Start Free Trial" in content.ctas

    def test_extracts_features(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert "Real-time collaboration" in content.features
        assert "Automated workflows" in content.features

    def test_extracts_raw_text(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com")
        assert "Ship Projects Faster" in content.raw_text

    def test_preserves_url(self) -> None:
        content = _parse_content(SAMPLE_HTML, "https://example.com/page")
        assert content.url == "https://example.com/page"

    def test_handles_empty_html(self) -> None:
        content = _parse_content("", "https://example.com")
        assert content.title == ""
        assert content.headings == []


class TestFetchPage:
    async def test_fetch_success(self) -> None:
        mock_response = httpx.Response(200, text=SAMPLE_HTML, request=httpx.Request("GET", "https://example.com"))

        with (
            patch("app.services.page_fetcher.validate_url", return_value="https://example.com"),
            patch("app.services.page_fetcher.httpx.AsyncClient") as mock_client_cls,
        ):
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            content = await fetch_page("https://example.com")
            assert content.title == "Best Project Management Tool"

    async def test_fetch_http_error(self) -> None:
        mock_response = httpx.Response(
            404,
            request=httpx.Request("GET", "https://example.com"),
        )

        with (
            patch("app.services.page_fetcher.validate_url", return_value="https://example.com"),
            patch("app.services.page_fetcher.httpx.AsyncClient") as mock_client_cls,
        ):
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(PageFetchError, match="HTTP 404"):
                await fetch_page("https://example.com")

    async def test_fetch_request_error(self) -> None:
        with (
            patch("app.services.page_fetcher.validate_url", return_value="https://example.com"),
            patch("app.services.page_fetcher.httpx.AsyncClient") as mock_client_cls,
        ):
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(PageFetchError, match="Request failed"):
                await fetch_page("https://example.com")
