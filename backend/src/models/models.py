"""
Các model cho database
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey,
    Enum, Numeric, Boolean, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class UserRole(str, PyEnum):
    """Vai trò người dùng"""
    CUSTOMER = "CUSTOMER"
    OWNER = "OWNER"


class BookingStatus(str, PyEnum):
    """Trạng thái booking"""
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, PyEnum):
    """Trạng thái thanh toán"""
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class ComplaintStatus(str, PyEnum):
    """Trạng thái khiếu nại"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class ComplaintType(str, PyEnum):
    """Loại khiếu nại"""
    WRONG_SEAT = "WRONG_SEAT"
    LATE = "LATE"
    DRIVER = "DRIVER"
    LOST_ITEM = "LOST_ITEM"
    PAYMENT = "PAYMENT"
    BOOKING_ERROR = "BOOKING_ERROR"
    REFUND = "REFUND"
    OTHER = "OTHER"


class ComplaintPriority(str, PyEnum):
    """Mức độ ưu tiên khiếu nại"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RefundStatus(str, PyEnum):
    """Trạng thái hoàn tiền"""
    REQUESTED = "REQUESTED"
    WAITING_OWNER_APPROVAL = "WAITING_OWNER_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REFUNDED = "REFUNDED"


class TripStatus(str, PyEnum):
    """Trạng thái chuyến xe"""
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class ActorType(str, PyEnum):
    """Loại actor trong audit log"""
    CUSTOMER = "CUSTOMER"
    OWNER = "OWNER"
    SYSTEM = "SYSTEM"


class User(Base):
    """Bảng người dùng"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id")
    complaints = relationship("Complaint", back_populates="customer", foreign_keys="Complaint.customer_id")

    __table_args__ = (
        Index("ix_users_role", "role"),
    )


class Trip(Base):
    """Bảng chuyến xe"""
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route = Column(String(255), nullable=False)  # Tên tuyến
    origin = Column(String(255), nullable=False)  # Điểm đi
    destination = Column(String(255), nullable=False)  # Điểm đến
    departure_time = Column(String(10), nullable=False)  # Giờ khởi hành
    arrival_time = Column(String(10), nullable=False)  # Giờ đến
    price = Column(Integer, nullable=False)  # Giá vé
    total_seats = Column(Integer, nullable=False)  # Tổng số ghế
    available_seats = Column(Integer, nullable=False)  # Số ghế trống
    status = Column(Enum(TripStatus), default=TripStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="trip")

    __table_args__ = (
        Index("ix_trips_route", "route"),
        Index("ix_trips_departure", "departure_time"),
        Index("ix_trips_status", "status"),
    )


class Booking(Base):
    """Bảng booking"""
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_code = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    seat_count = Column(Integer, nullable=False)  # Số ghế đặt
    total_amount = Column(Integer, nullable=False)  # Tổng tiền
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING_PAYMENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    trip = relationship("Trip", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    complaints = relationship("Complaint", back_populates="booking")
    refund_requests = relationship("RefundRequest", back_populates="booking")

    __table_args__ = (
        Index("ix_bookings_user", "user_id"),
        Index("ix_bookings_trip", "trip_id"),
        Index("ix_bookings_status", "status"),
        Index("ix_bookings_created", "created_at"),
    )


class Payment(Base):
    """Bảng thanh toán"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)
    method = Column(String(50), default="CASH")  # Phương thức thanh toán
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="payment")

    __table_args__ = (
        Index("ix_payments_booking", "booking_id"),
        Index("ix_payments_status", "status"),
    )


class Complaint(Base):
    """Bảng khiếu nại"""
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_code = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True)
    type = Column(Enum(ComplaintType), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN)
    priority = Column(Enum(ComplaintPriority), default=ComplaintPriority.MEDIUM)
    owner_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("User", back_populates="complaints", foreign_keys=[customer_id])
    booking = relationship("Booking", back_populates="complaints")
    refund_requests = relationship("RefundRequest", back_populates="complaint", uselist=False)

    __table_args__ = (
        Index("ix_complaints_customer", "customer_id"),
        Index("ix_complaints_booking", "booking_id"),
        Index("ix_complaints_status", "status"),
        Index("ix_complaints_priority", "priority"),
    )


class RefundRequest(Base):
    """Bảng yêu cầu hoàn tiền"""
    __tablename__ = "refund_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refund_code = Column(String(20), unique=True, nullable=False, index=True)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_holder = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(Enum(RefundStatus), default=RefundStatus.REQUESTED)
    owner_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complaint = relationship("Complaint", back_populates="refund_requests")
    booking = relationship("Booking", back_populates="refund_requests")

    __table_args__ = (
        Index("ix_refunds_complaint", "complaint_id"),
        Index("ix_refunds_booking", "booking_id"),
        Index("ix_refunds_status", "status"),
    )


class AuditLog(Base):
    """Bảng log kiểm toán"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_type = Column(Enum(ActorType), nullable=False)
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_action", "action"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_created", "created_at"),
    )
