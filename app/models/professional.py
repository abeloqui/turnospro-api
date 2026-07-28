from datetime import datetime, time
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Time, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[int] = mapped_column(primary_key=True)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(150))
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6")  # para el calendario
    bio: Mapped[str | None] = mapped_column(Text)

    # Horario laboral (simplificado para MVP)
    work_start: Mapped[time] = mapped_column(Time, default=time(9, 0))
    work_end: Mapped[time] = mapped_column(Time, default=time(18, 0))
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    clinic: Mapped["Clinic"] = relationship(back_populates="professionals")
    user: Mapped["User | None"] = relationship(back_populates="professional")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="professional")
