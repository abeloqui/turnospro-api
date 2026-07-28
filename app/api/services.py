from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.session import get_db
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceOut, ServiceCreate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ServiceOut])
async def list_services(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Service)
        .where(Service.clinic_id == current_user.clinic_id)
        .where(Service.is_active == True)
        .order_by(Service.name)
    )
    return result.scalars().all()


@router.get("/public/{clinic_slug}", response_model=List[ServiceOut])
async def list_services_public(
    clinic_slug: str,
    db: AsyncSession = Depends(get_db),
):
    from app.models.clinic import Clinic

    clinic = await db.execute(select(Clinic).where(Clinic.slug == clinic_slug))
    clinic_obj = clinic.scalar_one_or_none()
    if not clinic_obj:
        raise HTTPException(status_code=404, detail="Clínica no encontrada")

    result = await db.execute(
        select(Service)
        .where(Service.clinic_id == clinic_obj.id)
        .where(Service.is_active == True)
        .order_by(Service.name)
    )
    return result.scalars().all()
