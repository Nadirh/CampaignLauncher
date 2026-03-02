import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ad_group import AdGroup


class MatchType(str, enum.Enum):
    BROAD = "broad"
    PHRASE = "phrase"
    EXACT = "exact"


class Keyword(TimestampMixin, Base):
    __tablename__ = "keywords"

    text: Mapped[str] = mapped_column(String(255))
    match_type: Mapped[MatchType] = mapped_column(
        Enum(MatchType, native_enum=False),
        default=MatchType.BROAD,
    )
    bid: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    ad_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ad_groups.id", ondelete="CASCADE"),
    )

    ad_group: Mapped["AdGroup"] = relationship(back_populates="keywords")
