"""
Script de datos de demostración.
Ejecutar con: python -m app.db.seed
"""
import asyncio
from datetime import datetime, timedelta, time
from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models import Clinic, User, Professional, Patient, Service, Appointment
from app.models.user import UserRole
from app.models.appointment import AppointmentStatus
from app.core.security import get_password_hash
import secrets


async def seed():
    print("🗑️  Eliminando tablas anteriores...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Clínica
        clinic = Clinic(
            name="Clínica Demo Salud",
            slug="clinica-demo",
            phone="+54 11 4567-8900",
            email="info@clinicademo.com",
            address="Av. Ejemplo 1234, CABA",
        )
        db.add(clinic)
        await db.flush()

        # 2. Usuario Admin
        admin = User(
            clinic_id=clinic.id,
            email="admin@clinicademo.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin Demo",
            role=UserRole.ADMIN,
        )
        db.add(admin)

        # 3. Profesionales
        professionals_data = [
            {
                "full_name": "Dra. María González",
                "specialty": "Clínica Médica",
                "color": "#3B82F6",
                "work_start": time(9, 0),
                "work_end": time(13, 0),
                "slot_duration_minutes": 30,
            },
            {
                "full_name": "Dr. Carlos Ramírez",
                "specialty": "Cardiología",
                "color": "#EF4444",
                "work_start": time(14, 0),
                "work_end": time(18, 0),
                "slot_duration_minutes": 45,
            },
            {
                "full_name": "Lic. Ana Martínez",
                "specialty": "Nutrición",
                "color": "#10B981",
                "work_start": time(9, 0),
                "work_end": time(17, 0),
                "slot_duration_minutes": 40,
            },
        ]

        professionals = []
        for p in professionals_data:
            prof = Professional(clinic_id=clinic.id, **p)
            db.add(prof)
            professionals.append(prof)

        await db.flush()

        # 4. Servicios
        services_data = [
            {"name": "Consulta General", "duration_minutes": 30, "price": 15000, "color": "#3B82F6"},
            {"name": "Control Cardiológico", "duration_minutes": 45, "price": 25000, "color": "#EF4444"},
            {"name": "Consulta Nutricional", "duration_minutes": 40, "price": 18000, "color": "#10B981"},
            {"name": "Electrocardiograma", "duration_minutes": 20, "price": 12000, "color": "#8B5CF6"},
        ]

        services = []
        for s in services_data:
            serv = Service(clinic_id=clinic.id, **s)
            db.add(serv)
            services.append(serv)

        await db.flush()

        # 5. Pacientes
        patients_data = [
            {"full_name": "Juan Pérez", "phone": "+5491112345678", "email": "juan@email.com"},
            {"full_name": "Laura Fernández", "phone": "+5491187654321", "email": "laura@email.com"},
            {"full_name": "Martín López", "phone": "+5491199887766"},
            {"full_name": "Sofía Ruiz", "phone": "+5491177665544", "email": "sofia@email.com"},
            {"full_name": "Diego Torres", "phone": "+5491166554433"},
            {"full_name": "Valentina Castro", "phone": "+5491155443322"},
            {"full_name": "Mateo Silva", "phone": "+5491144332211"},
            {"full_name": "Camila Díaz", "phone": "+5491133221100"},
        ]

        patients = []
        for p in patients_data:
            patient = Patient(clinic_id=clinic.id, **p)
            db.add(patient)
            patients.append(patient)

        await db.flush()

        # 6. Turnos de ejemplo
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        appointments_data = [
            (professionals[0], patients[0], services[0], today + timedelta(hours=10), AppointmentStatus.CONFIRMED),
            (professionals[0], patients[1], services[0], today + timedelta(hours=11), AppointmentStatus.SCHEDULED),
            (professionals[2], patients[2], services[2], today + timedelta(hours=15), AppointmentStatus.SCHEDULED),
            (professionals[1], patients[3], services[1], today + timedelta(days=1, hours=15), AppointmentStatus.SCHEDULED),
            (professionals[1], patients[4], services[1], today + timedelta(days=1, hours=16), AppointmentStatus.SCHEDULED),
            (professionals[0], patients[5], services[0], today - timedelta(days=2, hours=-10), AppointmentStatus.COMPLETED),
            (professionals[2], patients[6], services[2], today - timedelta(days=1, hours=-11), AppointmentStatus.NO_SHOW),
        ]

        for prof, patient, service, start, status in appointments_data:
            end = start + timedelta(minutes=service.duration_minutes)
            appt = Appointment(
                clinic_id=clinic.id,
                professional_id=prof.id,
                patient_id=patient.id,
                service_id=service.id,
                start_datetime=start,
                end_datetime=end,
                status=status,
                public_token=secrets.token_urlsafe(32),
            )
            db.add(appt)

        await db.commit()
        print("✅ Base de datos sembrada correctamente")
        print("")
        print("🔑 Credenciales de acceso:")
        print("   Email:    admin@clinicademo.com")
        print("   Password: admin123")
        print("")
        print("🌐 Clínica slug para portal público: clinica-demo")


if __name__ == "__main__":
    asyncio.run(seed())
