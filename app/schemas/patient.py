from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class PatientBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    document_number: Optional[str] = None
    birth_date: Optional[date] = None
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    document_number: Optional[str] = None
    birth_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    is_active: bool
    created_at: datetime
