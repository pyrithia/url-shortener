import time

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, index=True)
    real_url: Mapped[str]
    created_at: Mapped[int] = mapped_column(default=lambda: int(time.time()))
    expires_at: Mapped[int]

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at
