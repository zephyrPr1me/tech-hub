from datetime import datetime
from pydantic import BaseModel


class RawPost(BaseModel):
    source_id: str
    title: str | None
    content: str
    url: str
    published_at: datetime
    raw_media: list[str] = []
