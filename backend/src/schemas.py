"""
Pydantic schemas cho API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from enum import Enum


# ============ ENUMS ============
class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    OWNER = "OWNER"


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class ComplaintStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class ComplaintType(str, Enum):
    WRONG_SEAT = "WRONG_SEAT"
    LATE = "LATE"
    DRIVER = "DRIVER"
    LOST_ITEM = "LOST_ITEM"
    PAYMENT = "PAYMENT"
    BOOKING_ERROR = "BOOKING_ERROR"
    REFUND = "REFUND"
    OTHER = "OTHER"


class ComplaintPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RefundStatus(str, Enum):
    REQUESTED = "REQUESTED"
    WAITING_OWNER_APPROVAL = "WAITING_OWNER_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REFUNDED = "REFUNDED"


class TripStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class ActorType(str, Enum):
    CUSTOMER = "CUSTOMER"
    OWNER = "OWNER"
    SYSTEM = "SYSTEM"


# ============ AUTH ============
class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str]
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ============ TRIP ============
class TripCreate(BaseModel):
    route: str = Field(..., min_length=1, max_length=255)
    origin: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)
    departure_time: str = Field(..., max_length=10)  # HH:MM
    arrival_time: str = Field(..., max_length=10)  # HH:MM
    price: int = Field(..., gt=0)
    total_seats: int = Field(..., gt=0)


class TripUpdate(BaseModel):
    route: Optional[str] = Field(None, max_length=255)
    origin: Optional[str] = Field(None, max_length=255)
    destination: Optional[str] = Field(None, max_length=255)
    departure_time: Optional[str] = Field(None, max_length=10)
    arrival_time: Optional[str] = Field(None, max_length=10)
    price: Optional[int] = Field(None, gt=0)
    total_seats: Optional[int] = Field(None, gt=0)


class TripResponse(BaseModel):
    id: UUID
    route: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: int
    total_seats: int
    available_seats: int
    status: TripStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ============ BOOKING ============
class BookingCreate(BaseModel):
    trip_id: UUID
    seat_count: int = Field(..., gt=0)


class BookingResponse(BaseModel):
    id: UUID
    booking_code: str
    user_id: UUID
    trip_id: UUID
    seat_count: int
    total_amount: int
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingDetailResponse(BookingResponse):
    trip: TripResponse
    payment: Optional["PaymentResponse"] = None


# ============ PAYMENT ============
class PaymentResponse(BaseModel):
    id: UUID
    booking_id: UUID
    amount: int
    method: str
    status: PaymentStatus
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentSimulate(BaseModel):
    success: bool = True


# ============ COMPLAINT ============
class ComplaintCreate(BaseModel):
    booking_id: Optional[UUID] = None
    type: ComplaintType
    description: str = Field(..., min_length=1)
    priority: ComplaintPriority = ComplaintPriority.MEDIUM


class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    owner_note: Optional[str] = None


class ComplaintResponse(BaseModel):
    id: UUID
    complaint_code: str
    customer_id: UUID
    booking_id: Optional[UUID]
    type: ComplaintType
    description: str
    status: ComplaintStatus
    priority: ComplaintPriority
    owner_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplaintDetailResponse(ComplaintResponse):
    booking: Optional[BookingResponse] = None
    refund_request: Optional["RefundResponse"] = None


# ============ REFUND ============
class RefundCreate(BaseModel):
    complaint_id: Optional[UUID] = None
    booking_id: UUID
    amount: int = Field(..., gt=0)
    bank_name: str = Field(..., min_length=1, max_length=100)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_holder: str = Field(..., min_length=1, max_length=255)
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    id: UUID
    refund_code: str
    complaint_id: Optional[UUID]
    booking_id: UUID
    amount: int
    bank_name: str
    account_number: str
    account_holder: str
    reason: Optional[str]
    status: RefundStatus
    owner_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RefundDetailResponse(RefundResponse):
    complaint: Optional[ComplaintResponse] = None
    booking: Optional[BookingResponse] = None


class RefundNote(BaseModel):
    note: str


# ============ AUDIT LOG ============
class AuditLogResponse(BaseModel):
    id: UUID
    actor_type: ActorType
    actor_id: Optional[UUID]
    action: str
    entity_type: str
    entity_id: Optional[UUID]
    description: Optional[str]
    extra_data: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ DASHBOARD / STATS ============
class DashboardStats(BaseModel):
    total_trips: int
    today_trips: int
    total_bookings: int
    today_bookings: int
    revenue: int
    pending_payments: int
    open_complaints: int
    pending_refunds: int


# Forward references
BookingDetailResponse.model_rebuild()
ComplaintDetailResponse.model_rebuild()
