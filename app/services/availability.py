from datetime import datetime, timedelta, time, date
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.professional import Professional
from app.models.appointment import Appointment, AppointmentStatus
from app.models.service import Service


async def get_available_slots(
    db: AsyncSession,
    professional_id: int,
    service_id: int,
    target_date: date,
) -> list[dict]:
    """
    Calcula los horarios disponibles de un profesional para un servicio en una fecha.
    Lógica simple y robusta para MVP.
    """

    # 1. Traer profesional y servicio
    professional = await db.get(Professional, professional_id)
    service = await db.get(Service, service_id)

    if not professional or not professional.is_active:
        return []
    if not service or not service.is_active:
        return []

    duration = timedelta(minutes=service.duration_minutes)
    work_start = datetime.combine(target_date, professional.work_start)
    work_end = datetime.combine(target_date, professional.work_end)

    # 2. Traer turnos existentes del profesional ese día (no cancelados)
    stmt = select(Appointment).where(
        and_(
            Appointment.professional_id == professional_id,
            Appointment.start_datetime >= work_start,
            Appointment.start_datetime < work_end + timedelta(days=1),
            Appointment.status.not_in([
                AppointmentStatus.CANCELLED,
                AppointmentStatus.RESCHEDULED,
            ]),
        )
    )
    result = await db.execute(stmt)
    existing_appointments = result.scalars().all()

    # 3. Generar todos los slots posibles
    slots = []
    current = work_start

    while current + duration <= work_end:
        slot_end = current + duration

        # Verificar si se solapa con algún turno existente
        overlaps = False
        for appt in existing_appointments:
            if current < appt.end_datetime and slot_end > appt.start_datetime:
                overlaps = True
                break

        if not overlaps:
            # No ofrecer slots en el pasado
            if current > datetime.utcnow():
                slots.append({
                    "start": current.isoformat(),
                    "end": slot_end.isoformat(),
                })

        # Avanzar según la duración del slot del profesional
        current += timedelta(minutes=professional.slot_duration_minutes)

    return slots
