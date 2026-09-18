"""
API Routes - Bookings
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User, UserRole, BookingStatus
from src.schemas import BookingCreate, BookingResponse, BookingDetailResponse
from src.services.booking_service import BookingService
from src.services.payment_service import PaymentService
from src.dependencies import get_current_user, require_role

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("", response_model=list[BookingResponse])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách booking của user hiện tại"""
    bookings = await BookingService.get_bookings_by_user(db, current_user.id)
    return bookings


@router.get("/all", response_model=list[BookingResponse])
async def get_all_bookings(
    status: Optional[BookingStatus] = Query(None, description="Lọc theo trạng thái"),
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy tất cả bookings (chỉ owner)"""
    bookings = await BookingService.get_all_bookings(db, status)
    return bookings


@router.get("/{booking_id}", response_model=BookingDetailResponse)
async def get_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết booking"""
    booking = await BookingService.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking không tồn tại")

    # Customer chỉ xem được booking của mình
    if current_user.role == UserRole.CUSTOMER and booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xem booking này")

    return booking


@router.post("", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo booking mới"""
    try:
        booking = await BookingService.create_booking(db, current_user.id, data)
        # Tạo payment record
        payment = await PaymentService.create_payment(db, booking.id)
        await db.commit()

        # Reload booking với relationships
        booking = await BookingService.get_booking_by_id(db, booking.id)
        return booking
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hủy booking"""
    try:
        booking = await BookingService.cancel_booking(db, booking_id, current_user.id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking không tồn tại")
        return booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
