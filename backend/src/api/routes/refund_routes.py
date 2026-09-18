"""
API Routes - Refunds
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User, UserRole
from src.schemas import RefundCreate, RefundResponse, RefundDetailResponse, RefundNote
from src.services.refund_service import RefundService
from src.services.booking_service import BookingService
from src.services.audit_service import AuditService
from src.services.complaint_service import ComplaintService
from src.dependencies import get_current_user, require_role
from src.models import ActorType

router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.get("", response_model=list[RefundResponse])
async def get_my_refunds(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách refund của user hiện tại"""
    refunds = await RefundService.get_refunds_by_customer(db, current_user.id)
    return refunds


@router.get("/pending", response_model=list[RefundDetailResponse])
async def get_pending_refunds(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy danh sách refund đang chờ duyệt (chỉ owner)"""
    from src.models import RefundStatus
    refunds = await RefundService.get_all_refunds(db, status=RefundStatus.WAITING_OWNER_APPROVAL)
    return refunds


@router.get("/all", response_model=list[RefundDetailResponse])
async def get_all_refunds(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy tất cả refunds (chỉ owner)"""
    refunds = await RefundService.get_all_refunds(db)
    return refunds


@router.get("/{refund_id}", response_model=RefundDetailResponse)
async def get_refund(
    refund_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết refund"""
    refund = await RefundService.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund không tồn tại")

    # Customer chỉ xem được refund liên quan đến booking của mình
    if current_user.role == UserRole.CUSTOMER:
        if not refund.booking or refund.booking.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền")

    return refund


@router.post("", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(
    data: RefundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo yêu cầu hoàn tiền"""
    # Kiểm tra booking thuộc về customer
    booking = await BookingService.get_booking_by_id(db, data.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking không tồn tại")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Booking không thuộc về bạn")

    # Kiểm tra complaint nếu có
    if data.complaint_id:
        complaint = await ComplaintService.get_complaint_by_id(db, data.complaint_id)
        if not complaint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khiếu nại không tồn tại")
        if complaint.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Khiếu nại không thuộc về bạn")

    refund = await RefundService.create_refund(db, current_user.id, data)
    return refund


@router.post("/{refund_id}/approve", response_model=RefundResponse)
async def approve_refund(
    refund_id: UUID,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Phê duyệt refund (chỉ owner)"""
    try:
        refund = await RefundService.approve_refund(db, refund_id, owner.id)
        if not refund:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund không tồn tại")
        return refund
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{refund_id}/reject", response_model=RefundResponse)
async def reject_refund(
    refund_id: UUID,
    data: RefundNote = Body(...),
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Từ chối refund (chỉ owner)"""
    try:
        refund = await RefundService.reject_refund(db, refund_id, owner.id, data.note)
        if not refund:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund không tồn tại")
        return refund
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{refund_id}/mark-refunded", response_model=RefundResponse)
async def mark_as_refunded(
    refund_id: UUID,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Đánh dấu đã hoàn tiền (chỉ owner)"""
    try:
        refund = await RefundService.mark_as_refunded(db, refund_id, owner.id)
        if not refund:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund không tồn tại")
        return refund
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
