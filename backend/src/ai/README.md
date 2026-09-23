# AI Tool Layer

## Tổng quan

AI Tool Layer là cầu nối giữa Agent và hệ thống nghiệp vụ hiện tại.

```
Agent
   ↓
Tool
   ↓
Service
   ↓
Database
```

## Cấu trúc

```
backend/src/ai/
├── __init__.py           # Export các Tools
├── tools/
│   ├── __init__.py       # Export các Tool classes
│   ├── trip_tools.py     # Tools cho domain chuyến xe
│   ├── booking_tools.py  # Tools cho domain đặt vé
│   ├── payment_tools.py  # Tools cho domain thanh toán
│   ├── complaint_tools.py # Tools cho domain khiếu nại
│   └── refund_tools.py   # Tools cho domain hoàn tiền
└── README.md
```

## Nguyên tắc

1. **Tool KHÔNG viết business logic** - chỉ gọi Service hiện có
2. **Tool nhận input, validate, check quyền, gọi Service, trả về kết quả**
3. **Tool luôn trả về Dict có cấu trúc** với fields: `success`, `error` (nếu có lỗi), và data tương ứng

## Các Tools

### TripTools

| Method | Mô tả |
|--------|--------|
| `search_trips()` | Tìm chuyến xe theo điểm đi, điểm đến |
| `get_trip()` | Lấy thông tin chi tiết một chuyến xe |
| `check_available_seats()` | Kiểm tra số ghế còn trống (REALTIME) |
| `get_available_trips_summary()` | Lấy danh sách chuyến xe còn ghế |

### BookingTools

| Method | Mô tả |
|--------|--------|
| `create_booking()` | Tạo booking mới |
| `get_booking()` | Lấy thông tin booking theo ID hoặc mã |
| `get_user_bookings()` | Lấy danh sách booking của khách hàng |
| `cancel_booking()` | Hủy booking |
| `get_all_bookings()` | Lấy tất cả bookings (cho owner) |

### PaymentTools

| Method | Mô tả |
|--------|--------|
| `create_payment()` | Tạo payment record cho booking |
| `process_payment()` | Xử lý thanh toán (mô phỏng) |
| `get_payment()` | Lấy thông tin payment |
| `get_pending_payments_count()` | Đếm số payment đang chờ |

### ComplaintTools

| Method | Mô tả |
|--------|--------|
| `create_complaint()` | Tạo khiếu nại mới |
| `get_complaint()` | Lấy thông tin khiếu nại |
| `get_customer_complaints()` | Lấy khiếu nại của khách hàng |
| `get_all_complaints()` | Lấy tất cả khiếu nại (cho owner) |
| `resolve_complaint()` | Giải quyết khiếu nại (owner) |
| `get_open_complaints_count()` | Đếm số khiếu nại đang mở |

### RefundTools

| Method | Mô tả |
|--------|--------|
| `create_refund_request()` | Tạo yêu cầu hoàn tiền |
| `get_refund()` | Lấy thông tin refund |
| `get_customer_refunds()` | Lấy refunds của khách hàng |
| `get_all_refunds()` | Lấy tất cả refunds (cho owner) |
| `approve_refund()` | Owner phê duyệt refund |
| `reject_refund()` | Owner từ chối refund |
| `mark_as_refunded()` | Owner đánh dấu đã hoàn tiền |
| `get_pending_refunds_count()` | Đếm số refund đang chờ |

## Ví dụ sử dụng

```python
from src.ai import TripTools, BookingTools
from src.database import async_session_maker

async def book_trip_example():
    async with async_session_maker() as db:
        # Search trips
        trip_tools = TripTools()
        result = await trip_tools.search_trips(
            db=db,
            origin="Sai Gon",
            destination="Da Lat"
        )
        
        if result["success"]:
            for trip in result["trips"]:
                print(f"Trip {trip['id']}: {trip['origin']} -> {trip['destination']}")
        
        # Check available seats
        seats_result = await trip_tools.check_available_seats(
            db=db,
            trip_id="<trip_uuid>",
            seat_count=2
        )
        
        # Create booking
        booking_tools = BookingTools()
        booking_result = await booking_tools.create_booking(
            db=db,
            user_id="<user_uuid>",
            trip_id="<trip_uuid>",
            seat_count=2
        )
```

## Response Format

Mọi Tool method đều trả về Dict với cấu trúc:

```python
# Thành công
{
    "success": True,
    "data_field": {...}  # hoặc list nếu là danh sách
}

# Thất bại
{
    "success": False,
    "error": "Mô tả lỗi"
}
```

## Chú ý quan trọng

1. **Dữ liệu REALTIME**: Các method như `check_available_seats()` luôn lấy dữ liệu từ Database, không dùng RAG hay hard-code.

2. **Authorization**: Một số action cần kiểm tra quyền (chỉ owner mới làm được).

3. **Audit Log**: Các action quan trọng đều được ghi log qua `AuditService`.

4. **Validation**: Input được validate trước khi gọi Service.
