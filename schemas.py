from datetime import UTC, datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, HttpUrl, field_validator


class UrlBase(BaseModel):
    real_url: HttpUrl
    expires_at: AwareDatetime | None = None


class UrlCreate(UrlBase):
    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, value):
        if value is not None and value <= datetime.now(UTC):
            raise ValueError("Expiry must be in the future")
        return value


class UrlResponse(UrlBase):
    id: int
    created_at: datetime
    code: str
    is_expired: bool

    model_config = ConfigDict(from_attributes=True)
