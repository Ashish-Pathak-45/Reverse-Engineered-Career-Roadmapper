from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ResourceOut(BaseModel):
    id: int
    title: str
    provider: str
    topic: str
    difficulty: str
    format: str
    is_free: bool
    cost_info: str
    source_url: str
    verified_date: str
    description: str
    created_at: datetime
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True
