from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int = 30
    price: Optional[float] = None
    color: str = "#10B981"


class ServiceCreate(ServiceBase):
    pass


class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    is_active: bool
    created_at: datetime
