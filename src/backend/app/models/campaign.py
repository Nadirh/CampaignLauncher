import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ad_group import AdGroup


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    LAUNCHED = "launched"
    PAUSED = "paused"


class BiddingStrategy(str, enum.Enum):
    MANUAL_CPC = "manual_cpc"
    MAXIMIZE_CLICKS = "maximize_clicks"
    MAXIMIZE_CONVERSIONS = "maximize_conversions"
    TARGET_CPA = "target_cpa"
    TARGET_ROAS = "target_roas"


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(255))
    landing_page_url: Mapped[str] = mapped_column(String(2048))
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, native_enum=False),
        default=CampaignStatus.DRAFT,
    )
    bidding_strategy: Mapped[BiddingStrategy] = mapped_column(
        Enum(BiddingStrategy, native_enum=False),
        default=BiddingStrategy.MANUAL_CPC,
    )
    daily_budget: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    ad_groups: Mapped[list["AdGroup"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
    )
