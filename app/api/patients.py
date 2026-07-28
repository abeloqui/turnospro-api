from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.session import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientOut, PatientCreate, PatientUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[PatientOut])
async def list_patients(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Patient)
        .where(Patient.clinic_id == current_user.clinic_id)
        .where(Patient.is_active == True)
        .order_by(Patient.full_name)
    )
    return result.scalars().all()


@router.post("/", response_model=PatientOut, status_code=201)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = Patient(**data.model_dump(), clinic_id=current_user.clinic_id)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Patient)
        .where(Patient.id == patient_id)
        .where(Patient.clinic_id == current_user.clinic_id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient
