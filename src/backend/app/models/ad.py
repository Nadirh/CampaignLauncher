import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ad_group import AdGroup


class Ad(TimestampMixin, Base):
    __tablename__ = "ads"

    final_url: Mapped[str] = mapped_column(String(2048))
    headlines: Mapped[list] = mapped_column(JSON, default=list)
    descriptions: Mapped[list] = mapped_column(JSON, default=list)
    path1: Mapped[str | None] = mapped_column(String(15), nullable=True)
    path2: Mapped[str | None] = mapped_column(String(15), nullable=True)
    ad_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ad_groups.id", ondelete="CASCADE"),
    )

    ad_group: Mapped["AdGroup"] = relationship(back_populates="ads")
