from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from .base import Base


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"       # Confirmado
    CONFIRMED = "confirmed"       # Paciente confirmó
    COMPLETED = "completed"       # Atendido
    CANCELLED = "cancelled"       # Cancelado
    NO_SHOW = "no_show"           # No se presentó
    RESCHEDULED = "rescheduled"   # Reprogramado


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"), index=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("professionals.id"), index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))

    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True
    )

    notes: Mapped[str | None] = mapped_column(Text)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)

    # Tokens para links mágicos (cancelar / confirmar sin login)
    public_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    reminder_24h_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_2h_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    clinic: Mapped["Clinic"] = relationship(back_populates="appointments")
    professional: Mapped["Professional"] = relationship(back_populates="appointments")
    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")
