import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.ad_group import AdGroup
from app.models.campaign import Campaign
from app.schemas.pipeline import CampaignGenerateResponse
from app.services.excel_export import generate_workbook

router = APIRouter(prefix="/api/campaigns", tags=["export"])

XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


@router.get("/{campaign_id}/export")
async def export_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    result = await db.execute(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(
            selectinload(Campaign.ad_groups).selectinload(AdGroup.keywords),
            selectinload(Campaign.ad_groups).selectinload(AdGroup.ads),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    response_model = CampaignGenerateResponse.model_validate(campaign)
    workbook_bytes = generate_workbook(response_model)
    filename = f"{campaign.name.replace(' ', '_')}.xlsx"

    return StreamingResponse(
        BytesIO(workbook_bytes),
        media_type=XLSX_CONTENT_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
