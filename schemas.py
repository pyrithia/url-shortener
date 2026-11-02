from datetime import datetime

from pydantic import AnyUrl, BaseModel, ConfigDict


class UrlBase(BaseModel):
    real_url: AnyUrl
    expires_at: datetime


class UrlCreate(UrlBase):
    pass


class UrlResponse(UrlBase):
    id: int
    created_at: datetime
    code: str
    is_expired: bool

    model_config = ConfigDict(from_attributes=True)
