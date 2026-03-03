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


def _build_user_message(
    content: PageContent,
    *,
    match_types: list[str] | None = None,
    negative_keywords: list[str] | None = None,
    bidding_strategy: str | None = None,
    bid_value: float | None = None,
    daily_budget: float | None = None,
    location_targeting: str | None = None,
) -> str:
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

    # Campaign settings section
    settings_lines: list[str] = []
    if bidding_strategy:
        settings_lines.append(f"Bidding Strategy: {bidding_strategy}")
    if bid_value is not None:
        settings_lines.append(f"Bid Value: ${bid_value}")
    if daily_budget is not None:
        settings_lines.append(f"Daily Budget: ${daily_budget}")
    if location_targeting:
        settings_lines.append(f"Location Targeting: {location_targeting}")
    if negative_keywords:
        settings_lines.append(f"Negative Keywords: {', '.join(negative_keywords)}")
    if settings_lines:
        parts.append("")
        parts.append("Campaign Settings:")
        parts.extend(settings_lines)

    # Determine match type instruction
    if match_types and len(match_types) > 0:
        match_label = " and ".join(match_types)
    else:
        match_label = "phrase and exact"

    parts.append("")
    parts.append("Based on this landing page content, generate a campaign structure.")
    parts.append(f"Use {match_label} match for each keyword.")
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
        {"text": "Headline text (30 chars max)", "position": 1, "trigger": "simplicity and efficiency"},
        {"text": "Another headline", "position": 2, "trigger": "social proof"}
      ],
      "descriptions": [
        {"text": "Description text (90 chars max)", "trigger": "reason why and loss aversion"}
      ]
    }
  ]
}
""")
    parts.append("Generate 3-5 tightly themed ad groups. Each ad group should have:")
    parts.append("- 5-10 keywords (each in both phrase and exact match)")
    parts.append("- 15 headlines (30 characters max each)")
    parts.append("- 4 descriptions (90 characters max each)")
    parts.append("Each headline and description must include a behavioral trigger label from the Behavioral Toolbox:")
    parts.append("  simplicity and efficiency, social proof, urgency and scarcity,")
    parts.append("  anticipation and exceptional benefit, reason why and loss aversion,")
    parts.append("  curiosity and information gaps, direct interaction")
    parts.append("Return ONLY the JSON object, no other text.")

    return "\n".join(parts)


def _extract_json(text: str) -> str:
    """Extract JSON from Claude's response, handling markdown code fences."""
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text.strip()


async def analyze_page(
    content: PageContent,
    *,
    match_types: list[str] | None = None,
    negative_keywords: list[str] | None = None,
    bidding_strategy: str | None = None,
    bid_value: float | None = None,
    daily_budget: float | None = None,
    location_targeting: str | None = None,
) -> CampaignStructure:
    """Send page content to Claude and parse the response into a CampaignStructure."""
    if not settings.ANTHROPIC_API_KEY:
        raise ClaudeAnalyzerError("ANTHROPIC_API_KEY is not configured")

    system_prompt = _load_system_prompt()
    user_message = _build_user_message(
        content,
        match_types=match_types,
        negative_keywords=negative_keywords,
        bidding_strategy=bidding_strategy,
        bid_value=bid_value,
        daily_budget=daily_budget,
        location_targeting=location_targeting,
    )

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
