import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ad import Ad
    from app.models.campaign import Campaign
    from app.models.keyword import Keyword


class AdGroup(TimestampMixin, Base):
    __tablename__ = "ad_groups"

    name: Mapped[str] = mapped_column(String(255))
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"),
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="ad_groups")
    keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="ad_group",
        cascade="all, delete-orphan",
    )
    ads: Mapped[list["Ad"]] = relationship(
        back_populates="ad_group",
        cascade="all, delete-orphan",
    )
