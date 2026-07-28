from datetime import time, datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProfessionalBase(BaseModel):
    full_name: str
    specialty: str
    phone: Optional[str] = None
    email: Optional[str] = None
    color: str = "#3B82F6"
    bio: Optional[str] = None
    work_start: time = time(9, 0)
    work_end: time = time(18, 0)
    slot_duration_minutes: int = 30


class ProfessionalCreate(ProfessionalBase):
    pass


class ProfessionalOut(ProfessionalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    is_active: bool
    created_at: datetime
