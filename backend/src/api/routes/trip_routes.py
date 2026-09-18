"""
API Routes - Trips
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User, UserRole, TripStatus
from src.schemas import TripCreate, TripUpdate, TripResponse
from src.services.trip_service import TripService
from src.dependencies import get_current_user, require_role

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("", response_model=list[TripResponse])
async def get_trips(
    origin: Optional[str] = Query(None, description="Lọc theo điểm đi"),
    destination: Optional[str] = Query(None, description="Lọc theo điểm đến"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách chuyến xe"""
    trips = await TripService.get_all_trips(db, origin, destination, TripStatus.ACTIVE)
    return trips


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết chuyến xe"""
    trip = await TripService.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chuyến xe không tồn tại")
    return trip


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    data: TripCreate,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Tạo chuyến xe mới (chỉ owner)"""
    trip = await TripService.create_trip(db, data)
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID,
    data: TripUpdate,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Cập nhật chuyến xe (chỉ owner)"""
    trip = await TripService.update_trip(db, trip_id, data)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chuyến xe không tồn tại")
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_trip(
    trip_id: UUID,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Hủy chuyến xe (chỉ owner)"""
    trip = await TripService.cancel_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chuyến xe không tồn tại")
