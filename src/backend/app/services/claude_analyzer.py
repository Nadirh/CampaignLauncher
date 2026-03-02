import json
import logging
import re
import time
from pathlib import Path

import anthropic

from app.core.config import settings
from app.schemas.pipeline import CampaignStructure, PageContent

logger = logging.getLogger(__name__)

def _resolve_system_prompt_path() -> Path:
    """Resolve system prompt path, checking config first then common locations."""
    if settings.SYSTEM_PROMPT_PATH:
        return Path(settings.SYSTEM_PROMPT_PATH)
    # Walk up from this file looking for docs/SystemPrompt.md
    current = Path(__file__).resolve().parent
    while current != current.parent:
        candidate = current / "docs" / "SystemPrompt.md"
        if candidate.exists():
            return candidate
        current = current.parent
    # Fallback for Docker container layout
    return Path("/app/docs/SystemPrompt.md")
MODEL = "claude-sonnet-4-20250514"


class ClaudeAnalyzerError(Exception):
    pass


def _load_system_prompt() -> str:
    path = _resolve_system_prompt_path()
    try:
        return path.read_text()
    except FileNotFoundError:
        raise ClaudeAnalyzerError(f"System prompt not found at {path}")


def _build_user_message(content: PageContent) -> str:
    parts = [
        f"Landing Page URL: {content.url}",
        f"Title: {content.title}",
        f"Meta Description: {content.meta_description}",
        f"Headings: {', '.join(content.headings) if content.headings else 'None found'}",
    ]
    if content.hero_text:
        parts.append(f"Hero Text: {content.hero_text}")
    if content.ctas:
        parts.append(f"CTAs: {', '.join(content.ctas)}")
    if content.features:
        parts.append(f"Features: {', '.join(content.features)}")
    parts.append(f"Page Text (truncated): {content.raw_text[:5000]}")

    parts.append("")
    parts.append("Based on this landing page content, generate a campaign structure.")
    parts.append("Use phrase match and exact match for each keyword.")
    parts.append("Return your response as a JSON object with this exact schema:")
    parts.append("""
{
  "ad_groups": [
    {
      "name": "Ad Group Name",
      "keywords": [
        {"text": "keyword phrase", "match_type": "phrase"},
        {"text": "keyword phrase", "match_type": "exact"}
      ],
      "headlines": [
        {"text": "Headline text (30 chars max)", "position": 1},
        {"text": "Another headline", "position": 2}
      ],
      "descriptions": [
        {"text": "Description text (90 chars max)"}
      ]
    }
  ]
}
""")
    parts.append("Generate 3-5 tightly themed ad groups. Each ad group should have:")
    parts.append("- 5-10 keywords (each in both phrase and exact match)")
    parts.append("- 15 headlines (30 characters max each)")
    parts.append("- 4 descriptions (90 characters max each)")
    parts.append("Return ONLY the JSON object, no other text.")

    return "\n".join(parts)


def _extract_json(text: str) -> str:
    """Extract JSON from Claude's response, handling markdown code fences."""
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text.strip()


async def analyze_page(content: PageContent) -> CampaignStructure:
    """Send page content to Claude and parse the response into a CampaignStructure."""
    if not settings.ANTHROPIC_API_KEY:
        raise ClaudeAnalyzerError("ANTHROPIC_API_KEY is not configured")

    system_prompt = _load_system_prompt()
    user_message = _build_user_message(content)

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    start = time.monotonic()
    logger.info("Calling Claude API", extra={"model": MODEL})

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APIError as exc:
        latency = time.monotonic() - start
        logger.error(
            "Claude API error",
            extra={"error": str(exc), "latency_ms": int(latency * 1000)},
        )
        raise ClaudeAnalyzerError(f"Claude API error: {exc}")

    latency = time.monotonic() - start
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    logger.info(
        "Claude API response received",
        extra={
            "model": MODEL,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": int(latency * 1000),
        },
    )

    raw_text = response.content[0].text
    json_str = _extract_json(raw_text)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Claude JSON response", extra={"raw": raw_text[:500]})
        raise ClaudeAnalyzerError(f"Invalid JSON from Claude: {exc}")

    try:
        structure = CampaignStructure.model_validate(data)
    except Exception as exc:
        logger.error("Failed to validate Claude response structure", extra={"error": str(exc)})
        raise ClaudeAnalyzerError(f"Invalid campaign structure from Claude: {exc}")

    return structure
