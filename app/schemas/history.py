from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TimeHistoryResponse(BaseModel):
    id: UUID
    project_id: UUID
    work_role: str
    clock_in: datetime
    clock_out: Optional[datetime]

    class Config:
        from_attributes = True
