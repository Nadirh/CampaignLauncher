import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignStatus
from app.services.campaign_saver import save_campaign_structure
from app.services.claude_analyzer import analyze_page
from app.services.page_fetcher import fetch_page

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    def __init__(self, message: str, step: str) -> None:
        super().__init__(message)
        self.step = step


async def run_pipeline(campaign: Campaign, db: AsyncSession) -> Campaign:
    """Run the full generation pipeline: fetch -> analyze -> save."""
    if campaign.status != CampaignStatus.DRAFT:
        raise PipelineError(
            f"Campaign must be in draft status to generate (current: {campaign.status.value})",
            step="validation",
        )

    pipeline_start = time.monotonic()
    logger.info("Pipeline started", extra={"campaign_id": str(campaign.id)})

    # Step 1: Fetch page
    step_start = time.monotonic()
    try:
        page_content = await fetch_page(campaign.landing_page_url)
    except Exception as exc:
        logger.error(
            "Pipeline failed at fetch step",
            extra={"campaign_id": str(campaign.id), "error": str(exc)},
        )
        raise PipelineError(str(exc), step="fetch")
    logger.info(
        "Pipeline fetch complete",
        extra={"campaign_id": str(campaign.id), "latency_ms": int((time.monotonic() - step_start) * 1000)},
    )

    # Step 2: Analyze with Claude
    step_start = time.monotonic()
    try:
        structure = await analyze_page(page_content)
    except Exception as exc:
        logger.error(
            "Pipeline failed at analyze step",
            extra={"campaign_id": str(campaign.id), "error": str(exc)},
        )
        raise PipelineError(str(exc), step="analyze")
    logger.info(
        "Pipeline analyze complete",
        extra={"campaign_id": str(campaign.id), "latency_ms": int((time.monotonic() - step_start) * 1000)},
    )

    # Step 3: Save to database
    step_start = time.monotonic()
    try:
        campaign = await save_campaign_structure(campaign, structure, db)
    except Exception as exc:
        logger.error(
            "Pipeline failed at save step",
            extra={"campaign_id": str(campaign.id), "error": str(exc)},
        )
        raise PipelineError(str(exc), step="save")
    logger.info(
        "Pipeline save complete",
        extra={"campaign_id": str(campaign.id), "latency_ms": int((time.monotonic() - step_start) * 1000)},
    )

    total_ms = int((time.monotonic() - pipeline_start) * 1000)
    logger.info(
        "Pipeline completed",
        extra={"campaign_id": str(campaign.id), "total_latency_ms": total_ms},
    )

    return campaign
