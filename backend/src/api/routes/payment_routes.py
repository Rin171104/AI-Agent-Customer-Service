"""
API Routes - Payments
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User, UserRole
from src.schemas import PaymentResponse, PaymentSimulate
from src.services.payment_service import PaymentService
from src.services.booking_service import BookingService
from src.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy thông tin payment"""
    payment = await PaymentService.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment không tồn tại")

    # Kiểm tra quyền - customer chỉ xem payment của booking mình
    if current_user.role == UserRole.CUSTOMER:
        booking = await BookingService.get_booking_by_id(db, payment.booking_id)
        if not booking or booking.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền")

    return payment


@router.post("/{payment_id}/pay", response_model=PaymentResponse)
async def simulate_payment(
    payment_id: UUID,
    data: PaymentSimulate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mô phỏng thanh toán"""
    payment = await PaymentService.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment không tồn tại")

    # Kiểm tra quyền
    booking = await BookingService.get_booking_by_id(db, payment.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking không tồn tại")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền thanh toán booking này")

    try:
        actor_type = UserRole.CUSTOMER if current_user.role == UserRole.CUSTOMER else UserRole.OWNER
        payment = await PaymentService.process_payment(
            db,
            payment_id,
            success=data.success,
            actor_type=actor_type,
            actor_id=current_user.id
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
