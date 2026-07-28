from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    professional_id: int
    patient_id: int
    service_id: int
    start_datetime: datetime
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class AppointmentOut(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    end_datetime: datetime
    status: AppointmentStatus
    public_token: str
    reminder_24h_sent: bool
    reminder_2h_sent: bool
    created_at: datetime
    updated_at: datetime

    # Relaciones anidadas (opcionales para listados)
    professional_name: Optional[str] = None
    patient_name: Optional[str] = None
    service_name: Optional[str] = None


class AvailableSlot(BaseModel):
    start: datetime
    end: datetime


class AvailabilityRequest(BaseModel):
    professional_id: int
    service_id: int
    date: datetime = Field(..., description="Fecha para la cual se buscan slots (solo día)")
