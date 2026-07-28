from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from .base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    RECEPTIONIST = "receptionist"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"), index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(150))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.RECEPTIONIST)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    clinic: Mapped["Clinic"] = relationship(back_populates="users")
    professional: Mapped["Professional | None"] = relationship(back_populates="user", uselist=False)
