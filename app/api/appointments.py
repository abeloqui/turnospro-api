from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, date
import secrets
import httpx

from app.db.session import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.professional import Professional
from app.models.service import Service
from app.models.user import User
from app.models.clinic import Clinic
from app.schemas.appointment import (
    AppointmentOut,
    AppointmentCreate,
    AppointmentUpdate,
    AvailableSlot,
)
from app.services.availability import get_available_slots
from app.api.deps import get_current_user
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


async def notify_n8n(webhook_path: str, payload: dict):
    """Envía evento a n8n (no bloquea si falla)"""
    try:
        url = f"{settings.N8N_WEBHOOK_BASE_URL}{webhook_path}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception:
        pass  # Silenciar errores de n8n en MVP


@router.get("/", response_model=List[AppointmentOut])
async def list_appointments(
    date_from: date | None = None,
    date_to: date | None = None,
    professional_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Appointment)
        .options(
            selectinload(Appointment.professional),
            selectinload(Appointment.patient),
            selectinload(Appointment.service),
        )
        .where(Appointment.clinic_id == current_user.clinic_id)
    )

    if date_from:
        query = query.where(Appointment.start_datetime >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Appointment.start_datetime <= datetime.combine(date_to, datetime.max.time()))
    if professional_id:
        query = query.where(Appointment.professional_id == professional_id)

    query = query.order_by(Appointment.start_datetime)

    result = await db.execute(query)
    appointments = result.scalars().all()

    # Enriquecer respuesta
    output = []
    for appt in appointments:
        data = AppointmentOut.model_validate(appt)
        data.professional_name = appt.professional.full_name if appt.professional else None
        data.patient_name = appt.patient.full_name if appt.patient else None
        data.service_name = appt.service.name if appt.service else None
        output.append(data)

    return output


@router.post("/", response_model=AppointmentOut, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validar que existan las entidades
    professional = await db.get(Professional, data.professional_id)
    patient = await db.get(Patient, data.patient_id)
    service = await db.get(Service, data.service_id)

    if not professional or professional.clinic_id != current_user.clinic_id:
        raise HTTPException(status_code=400, detail="Profesional inválido")
    if not patient or patient.clinic_id != current_user.clinic_id:
        raise HTTPException(status_code=400, detail="Paciente inválido")
    if not service or service.clinic_id != current_user.clinic_id:
        raise HTTPException(status_code=400, detail="Servicio inválido")

    end_datetime = data.start_datetime + __import__("datetime").timedelta(minutes=service.duration_minutes)

    appointment = Appointment(
        clinic_id=current_user.clinic_id,
        professional_id=data.professional_id,
        patient_id=data.patient_id,
        service_id=data.service_id,
        start_datetime=data.start_datetime,
        end_datetime=end_datetime,
        notes=data.notes,
        public_token=secrets.token_urlsafe(32),
        status=AppointmentStatus.SCHEDULED,
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    # Notificar a n8n en background
    background_tasks.add_task(
        notify_n8n,
        settings.N8N_APPOINTMENT_CREATED_WEBHOOK,
        {
            "appointment_id": appointment.id,
            "patient_name": patient.full_name,
            "patient_phone": patient.phone,
            "professional_name": professional.full_name,
            "service_name": service.name,
            "start_datetime": appointment.start_datetime.isoformat(),
            "public_token": appointment.public_token,
            "frontend_url": settings.PUBLIC_FRONTEND_URL,
        },
    )

    return appointment


@router.get("/availability")
async def check_availability(
    professional_id: int,
    service_id: int,
    target_date: date,
    db: AsyncSession = Depends(get_db),
):
    """Endpoint público de disponibilidad"""
    slots = await get_available_slots(db, professional_id, service_id, target_date)
    return {"slots": slots}


@router.get("/public/{token}")
async def get_appointment_by_token(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Appointment)
        .options(
            selectinload(Appointment.professional),
            selectinload(Appointment.patient),
            selectinload(Appointment.service),
        )
        .where(Appointment.public_token == token)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    return {
        "id": appointment.id,
        "start_datetime": appointment.start_datetime,
        "end_datetime": appointment.end_datetime,
        "status": appointment.status,
        "professional_name": appointment.professional.full_name,
        "service_name": appointment.service.name,
        "patient_name": appointment.patient.full_name,
    }


@router.post("/public/{token}/cancel")
async def cancel_appointment_public(
    token: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Appointment).where(Appointment.public_token == token))
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    if appointment.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="El turno ya no se puede cancelar")

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancellation_reason = "Cancelado por el paciente"
    await db.commit()

    background_tasks.add_task(
        notify_n8n,
        settings.N8N_APPOINTMENT_CANCELLED_WEBHOOK,
        {
            "appointment_id": appointment.id,
            "public_token": token,
        },
    )

    return {"message": "Turno cancelado correctamente"}
