from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.session import get_db
from app.models.professional import Professional
from app.models.user import User
from app.schemas.professional import ProfessionalOut, ProfessionalCreate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProfessionalOut])
async def list_professionals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Professional)
        .where(Professional.clinic_id == current_user.clinic_id)
        .where(Professional.is_active == True)
        .order_by(Professional.full_name)
    )
    return result.scalars().all()


@router.get("/public/{clinic_slug}", response_model=List[ProfessionalOut])
async def list_professionals_public(
    clinic_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Endpoint público para el portal de reservas"""
    from app.models.clinic import Clinic

    clinic = await db.execute(select(Clinic).where(Clinic.slug == clinic_slug))
    clinic_obj = clinic.scalar_one_or_none()
    if not clinic_obj:
        raise HTTPException(status_code=404, detail="Clínica no encontrada")

    result = await db.execute(
        select(Professional)
        .where(Professional.clinic_id == clinic_obj.id)
        .where(Professional.is_active == True)
        .order_by(Professional.full_name)
    )
    return result.scalars().all()


@router.post("/", response_model=ProfessionalOut, status_code=201)
async def create_professional(
    data: ProfessionalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    professional = Professional(**data.model_dump(), clinic_id=current_user.clinic_id)
    db.add(professional)
    await db.commit()
    await db.refresh(professional)
    return professional
