"""
Seed data - tao du lieu mau
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from datetime import datetime, timedelta, timezone
import random

from src.database import async_session_maker, init_db
from src.models import User, Trip, Booking, Payment, Complaint, RefundRequest, AuditLog
from src.models import UserRole, BookingStatus, PaymentStatus, ComplaintStatus, ComplaintType, ComplaintPriority, RefundStatus, ActorType
from src.services.auth_service import AuthService


async def seed_database():
    """Tạo dữ liệu mẫu"""
    await init_db()

    async with async_session_maker() as db:
        # Tạo Owner
        owner = User(
            email="owner@hienhuu.vn",
            password_hash=AuthService.hash_password("Owner@123"),
            name="Nguyễn Văn Chủ",
            phone="0909123456",
            role=UserRole.OWNER
        )
        db.add(owner)

        # Tạo Customers
        customers_data = [
            {"email": "customer@example.com", "name": "Trần Thị Khách", "phone": "0912345678"},
            {"email": "khach2@example.com", "name": "Lê Văn Hai", "phone": "0923456789"},
            {"email": "khach3@example.com", "name": "Phạm Thị Ba", "phone": "0934567890"},
        ]
        customers = []
        for data in customers_data:
            customer = User(
                email=data["email"],
                password_hash=AuthService.hash_password("Customer@123"),
                name=data["name"],
                phone=data["phone"],
                role=UserRole.CUSTOMER
            )
            db.add(customer)
            customers.append(customer)

        await db.flush()

        # Tạo Trips
        trips_data = [
            {"route": "HN-TXS", "origin": "Hà Nội", "destination": "Tà Xùa", "departure_time": "06:00", "arrival_time": "10:00", "price": 350000, "total_seats": 40},
            {"route": "HN-TXS", "origin": "Hà Nội", "destination": "Tà Xùa", "departure_time": "08:00", "arrival_time": "12:00", "price": 350000, "total_seats": 40},
            {"route": "HN-TXS", "origin": "Hà Nội", "destination": "Tà Xùa", "departure_time": "14:00", "arrival_time": "18:00", "price": 350000, "total_seats": 40},
            {"route": "TXS-HN", "origin": "Tà Xùa", "destination": "Hà Nội", "departure_time": "07:00", "arrival_time": "11:00", "price": 350000, "total_seats": 40},
            {"route": "TXS-HN", "origin": "Tà Xùa", "destination": "Hà Nội", "departure_time": "13:00", "arrival_time": "17:00", "price": 350000, "total_seats": 40},
        ]
        trips = []
        for data in trips_data:
            trip = Trip(
                route=data["route"],
                origin=data["origin"],
                destination=data["destination"],
                departure_time=data["departure_time"],
                arrival_time=data["arrival_time"],
                price=data["price"],
                total_seats=data["total_seats"],
                available_seats=data["total_seats"],
            )
            db.add(trip)
            trips.append(trip)

        await db.flush()

        # Tạo Bookings
        booking1 = Booking(
            booking_code="BK100001",
            user_id=customers[0].id,
            trip_id=trips[0].id,
            seat_count=2,
            total_amount=trips[0].price * 2,
            status=BookingStatus.CONFIRMED
        )
        db.add(booking1)

        booking2 = Booking(
            booking_code="BK100002",
            user_id=customers[0].id,
            trip_id=trips[1].id,
            seat_count=1,
            total_amount=trips[1].price,
            status=BookingStatus.PENDING_PAYMENT
        )
        db.add(booking2)

        booking3 = Booking(
            booking_code="BK100003",
            user_id=customers[1].id,
            trip_id=trips[2].id,
            seat_count=3,
            total_amount=trips[2].price * 3,
            status=BookingStatus.CONFIRMED
        )
        db.add(booking3)

        booking4 = Booking(
            booking_code="BK100004",
            user_id=customers[2].id,
            trip_id=trips[3].id,
            seat_count=2,
            total_amount=trips[3].price * 2,
            status=BookingStatus.PENDING_PAYMENT
        )
        db.add(booking4)

        await db.flush()

        # Tạo Payments
        payment1 = Payment(
            booking_id=booking1.id,
            amount=booking1.total_amount,
            method="CASH",
            status=PaymentStatus.PAID,
            paid_at=datetime.now(timezone.utc)
        )
        db.add(payment1)

        payment3 = Payment(
            booking_id=booking3.id,
            amount=booking3.total_amount,
            method="CASH",
            status=PaymentStatus.PAID,
            paid_at=datetime.now(timezone.utc)
        )
        db.add(payment3)

        # Cập nhật available_seats
        trips[0].available_seats -= 2
        trips[2].available_seats -= 3

        await db.flush()

        # Tạo Complaints
        complaint1 = Complaint(
            complaint_code="CL100001",
            customer_id=customers[1].id,
            booking_id=booking3.id,
            type=ComplaintType.LATE,
            description="Xe đến trễ 30 phút so với giờ khởi hành",
            status=ComplaintStatus.OPEN,
            priority=ComplaintPriority.MEDIUM
        )
        db.add(complaint1)

        complaint2 = Complaint(
            complaint_code="CL100002",
            customer_id=customers[0].id,
            booking_id=None,
            type=ComplaintType.OTHER,
            description="Tôi muốn hỏi về chính sách hủy vé",
            status=ComplaintStatus.OPEN,
            priority=ComplaintPriority.LOW
        )
        db.add(complaint2)

        await db.flush()

        # Tạo Refund Requests
        refund1 = RefundRequest(
            refund_code="RF100001",
            complaint_id=complaint1.id,
            booking_id=booking3.id,
            amount=350000,
            bank_name="Vietcombank",
            account_number="1234567890",
            account_holder="Lê Văn Hai",
            reason="Xe đến trễ gây ảnh hưởng đến công việc",
            status=RefundStatus.WAITING_OWNER_APPROVAL
        )
        db.add(refund1)

        await db.flush()

        # Tạo Audit Logs
        audit1 = AuditLog(
            actor_type=ActorType.CUSTOMER,
            actor_id=customers[0].id,
            action="CREATE_BOOKING",
            entity_type="Booking",
            entity_id=booking1.id,
            description=f"Tạo booking {booking1.booking_code}",
        )
        db.add(audit1)

        audit2 = AuditLog(
            actor_type=ActorType.CUSTOMER,
            actor_id=customers[0].id,
            action="PAYMENT_SUCCESS",
            entity_type="Payment",
            entity_id=payment1.id,
            description=f"Thanh toán thành công {payment1.amount:,} VND",
            metadata={"booking_code": booking1.booking_code}
        )
        db.add(audit2)

        audit3 = AuditLog(
            actor_type=ActorType.CUSTOMER,
            actor_id=customers[1].id,
            action="CREATE_COMPLAINT",
            entity_type="Complaint",
            entity_id=complaint1.id,
            description=f"Tạo khiếu nại {complaint1.complaint_code}",
            metadata={"type": complaint1.type.value}
        )
        db.add(audit3)

        audit4 = AuditLog(
            actor_type=ActorType.CUSTOMER,
            actor_id=customers[1].id,
            action="CREATE_REFUND",
            entity_type="RefundRequest",
            entity_id=refund1.id,
            description=f"Yêu cầu hoàn tiền {refund1.refund_code}",
            metadata={"amount": refund1.amount}
        )
        db.add(audit4)

        await db.commit()
        print("✅ Seed data created successfully!")
        print("\n📋 Demo Accounts:")
        print("  Owner: owner@hienhuu.vn / Owner@123")
        print("  Customer: customer@example.com / Customer@123")
        print("\n📊 Sample Data:")
        print(f"  - {len(customers)} customers")
        print(f"  - {len(trips)} trips")
        print(f"  - 4 bookings (2 confirmed, 2 pending)")
        print(f"  - 2 payments (paid)")
        print(f"  - 2 complaints (open)")
        print(f"  - 1 refund request (waiting approval)")


if __name__ == "__main__":
    asyncio.run(seed_database())
