import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.campaign import Campaign
from app.schemas.ads_script import ScriptGenerateResponse
from app.services.ads_script_generator import generate_script
from app.services.excel_parser import ExcelParseError, parse_workbook

router = APIRouter(prefix="/api/campaigns", tags=["ads-script"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("/{campaign_id}/ads-script", response_model=ScriptGenerateResponse)
async def generate_ads_script(
    campaign_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> ScriptGenerateResponse:
    # Validate campaign exists
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Validate file type
    if file.content_type != XLSX_CONTENT_TYPE and not (
        file.filename and file.filename.endswith(".xlsx")
    ):
        raise HTTPException(status_code=400, detail="File must be an .xlsx Excel workbook")

    # Read and validate file size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Parse workbook
    try:
        parsed = parse_workbook(file_bytes)
    except ExcelParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Generate script
    script = generate_script(parsed)

    ad_groups = set()
    for kw in parsed.keywords:
        ad_groups.add(kw.ad_group)
    for ad in parsed.ads:
        ad_groups.add(ad.ad_group)

    return ScriptGenerateResponse(
        script=script,
        campaign_name=parsed.campaign.name,
        ad_group_count=len(ad_groups),
        keyword_count=len(parsed.keywords),
        ad_count=len(parsed.ads),
    )
