"""
API Routes - Complaints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User, UserRole, ComplaintStatus, ComplaintPriority
from src.schemas import ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintDetailResponse
from src.services.complaint_service import ComplaintService
from src.services.booking_service import BookingService
from src.dependencies import get_current_user, require_role

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.get("", response_model=list[ComplaintResponse])
async def get_my_complaints(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách khiếu nại của user hiện tại"""
    complaints = await ComplaintService.get_complaints_by_customer(db, current_user.id)
    return complaints


@router.get("/all", response_model=list[ComplaintDetailResponse])
async def get_all_complaints(
    status: Optional[ComplaintStatus] = Query(None, description="Lọc theo trạng thái"),
    priority: Optional[ComplaintPriority] = Query(None, description="Lọc theo mức ưu tiên"),
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy tất cả khiếu nại (chỉ owner)"""
    complaints = await ComplaintService.get_all_complaints(db, status, priority)
    return complaints


@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
async def get_complaint(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết khiếu nại"""
    complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khiếu nại không tồn tại")

    # Customer chỉ xem được khiếu nại của mình
    if current_user.role == UserRole.CUSTOMER and complaint.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xem khiếu nại này")

    return complaint


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    data: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo khiếu nại mới"""
    # Nếu có booking_id, kiểm tra booking thuộc về customer
    if data.booking_id:
        booking = await BookingService.get_booking_by_id(db, data.booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking không tồn tại")
        if booking.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Booking không thuộc về bạn")

    complaint = await ComplaintService.create_complaint(db, current_user.id, data)
    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: UUID,
    data: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Cập nhật khiếu nại (chỉ owner)"""
    complaint = await ComplaintService.update_complaint(db, complaint_id, data)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khiếu nại không tồn tại")
    return complaint


@router.post("/{complaint_id}/resolve", response_model=ComplaintResponse)
async def resolve_complaint(
    complaint_id: UUID,
    note: str,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Giải quyết khiếu nại (chỉ owner)"""
    complaint = await ComplaintService.resolve_complaint(db, complaint_id, note)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khiếu nại không tồn tại")
    return complaint
