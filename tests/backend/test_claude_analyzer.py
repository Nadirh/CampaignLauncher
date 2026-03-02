import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.pipeline import PageContent
from app.services.claude_analyzer import (
    ClaudeAnalyzerError,
    _build_user_message,
    _extract_json,
    _load_system_prompt,
    analyze_page,
)


SAMPLE_PAGE = PageContent(
    url="https://example.com",
    title="Example Product",
    meta_description="The best product ever.",
    headings=["Ship Faster", "Features", "Pricing"],
    hero_text="Ship your projects faster with our tool.",
    ctas=["Get Started"],
    features=["Real-time sync", "Automation"],
    raw_text="Ship your projects faster with our tool.",
)

VALID_RESPONSE_JSON = {
    "ad_groups": [
        {
            "name": "Project Management",
            "keywords": [
                {"text": "project management tool", "match_type": "phrase"},
                {"text": "project management tool", "match_type": "exact"},
            ],
            "headlines": [
                {"text": "Ship Projects Faster", "position": 1},
                {"text": "All-in-One PM Tool", "position": 2},
            ],
            "descriptions": [
                {"text": "Manage projects with real-time collaboration. Get started free today."},
            ],
        }
    ]
}


class TestExtractJson:
    def test_plain_json(self) -> None:
        raw = json.dumps({"ad_groups": []})
        assert _extract_json(raw) == raw

    def test_json_with_code_fence(self) -> None:
        raw = '```json\n{"ad_groups": []}\n```'
        assert _extract_json(raw) == '{"ad_groups": []}'

    def test_json_with_plain_code_fence(self) -> None:
        raw = '```\n{"ad_groups": []}\n```'
        assert _extract_json(raw) == '{"ad_groups": []}'

    def test_json_with_surrounding_text(self) -> None:
        raw = 'Here is the result:\n```json\n{"ad_groups": []}\n```\nDone.'
        assert _extract_json(raw) == '{"ad_groups": []}'


class TestBuildUserMessage:
    def test_includes_url(self) -> None:
        msg = _build_user_message(SAMPLE_PAGE)
        assert "https://example.com" in msg

    def test_includes_title(self) -> None:
        msg = _build_user_message(SAMPLE_PAGE)
        assert "Example Product" in msg

    def test_includes_headings(self) -> None:
        msg = _build_user_message(SAMPLE_PAGE)
        assert "Ship Faster" in msg

    def test_includes_features(self) -> None:
        msg = _build_user_message(SAMPLE_PAGE)
        assert "Real-time sync" in msg

    def test_includes_json_schema(self) -> None:
        msg = _build_user_message(SAMPLE_PAGE)
        assert "ad_groups" in msg


class TestLoadSystemPrompt:
    def test_loads_file(self) -> None:
        prompt = _load_system_prompt()
        assert "Search Ad Strategist" in prompt

    def test_raises_on_missing_file(self) -> None:
        with patch(
            "app.services.claude_analyzer._resolve_system_prompt_path",
            return_value=Path("/nonexistent/SystemPrompt.md"),
        ):
            with pytest.raises(ClaudeAnalyzerError, match="System prompt not found"):
                _load_system_prompt()


class TestAnalyzePage:
    async def test_success(self) -> None:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(VALID_RESPONSE_JSON))]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.claude_analyzer.settings") as mock_settings,
            patch("app.services.claude_analyzer.anthropic.AsyncAnthropic", return_value=mock_client),
        ):
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.SYSTEM_PROMPT_PATH = ""
            result = await analyze_page(SAMPLE_PAGE)

        assert len(result.ad_groups) == 1
        assert result.ad_groups[0].name == "Project Management"

    async def test_code_fence_response(self) -> None:
        fenced = f"```json\n{json.dumps(VALID_RESPONSE_JSON)}\n```"
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=fenced)]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.claude_analyzer.settings") as mock_settings,
            patch("app.services.claude_analyzer.anthropic.AsyncAnthropic", return_value=mock_client),
        ):
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.SYSTEM_PROMPT_PATH = ""
            result = await analyze_page(SAMPLE_PAGE)

        assert len(result.ad_groups) == 1

    async def test_missing_api_key(self) -> None:
        with patch("app.services.claude_analyzer.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = ""
            mock_settings.SYSTEM_PROMPT_PATH = ""
            with pytest.raises(ClaudeAnalyzerError, match="ANTHROPIC_API_KEY"):
                await analyze_page(SAMPLE_PAGE)

    async def test_invalid_json_response(self) -> None:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not JSON at all")]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.claude_analyzer.settings") as mock_settings,
            patch("app.services.claude_analyzer.anthropic.AsyncAnthropic", return_value=mock_client),
        ):
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.SYSTEM_PROMPT_PATH = ""
            with pytest.raises(ClaudeAnalyzerError, match="Invalid JSON"):
                await analyze_page(SAMPLE_PAGE)

    async def test_api_error(self) -> None:
        import anthropic as anthropic_mod

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic_mod.APIError(
                message="Rate limited",
                request=MagicMock(),
                body=None,
            )
        )

        with (
            patch("app.services.claude_analyzer.settings") as mock_settings,
            patch("app.services.claude_analyzer.anthropic.AsyncAnthropic", return_value=mock_client),
        ):
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.SYSTEM_PROMPT_PATH = ""
            with pytest.raises(ClaudeAnalyzerError, match="Claude API error"):
                await analyze_page(SAMPLE_PAGE)
