from datetime import UTC, datetime

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, index=True)
    real_url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    expires_at: Mapped[datetime]

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at.replace(tzinfo=UTC)
