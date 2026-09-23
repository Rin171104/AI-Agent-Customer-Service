# AI20K - Hiền Hựu Bus Customer Service & Operations Platform

> Hệ thống AI Multi-Agent hỗ trợ CSKH và vận hành cho Nhà xe Hiền Hựu
>
> **MVP Demo** - Chưa tích hợp AI/LLM, tập trung vào REST API và business logic hoàn chỉnh

---

## Mục lục

1. [Tổng quan](#tổng-quan)
2. [Kiến trúc](#kiến-trúc)
3. [Tech Stack](#tech-stack)
4. [Cấu trúc dự án](#cấu-trúc-dự-án)
5. [Docker Deployment](#docker-deployment)
6. [Development Local](#development-local)
7. [Tài khoản Demo](#tài-khoản-demo)
8. [API Endpoints](#api-endpoints)
9. [Luồng Demo chính](#luồng-demo-chính)
10. [AI-Ready Architecture](#ai-ready-architecture)

---

## Tổng quan

Hệ thống MVP với:

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: JWT với role-based access

### Vai trò người dùng

| Vai trò | Mô tả |
|---------|--------|
| **Customer** | Khách hàng đặt vé, xem booking, tạo khiếu nại, yêu cầu hoàn tiền |
| **Owner** | Chủ nhà xe quản lý chuyến xe, duyệt hoàn tiền, xem audit log |

---

## Kiến trúc

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Nginx :3000)                   │
│  Customer Dashboard │ Owner Dashboard │ Trips │ Bookings       │
└────────────────────────────┬────────────────────────────────┘
                             │ /api
┌────────────────────────────▼────────────────────────────────┐
│                   Backend (FastAPI :8000)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   Auth   │ │  Trips   │ │ Bookings │ │Payments  │       │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Complaints│ │ Refunds  │ │  Audit   │ │Dashboard │       │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│               PostgreSQL (:5432)                             │
│  users │ trips │ bookings │ payments │ complaints │ refunds │
│  audit_logs                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Validation
- **asyncpg** - PostgreSQL async driver
- **JWT** - Authentication

### Frontend
- **React 18**
- **TypeScript**
- **Vite**
- **Tailwind CSS**
- **React Router**
- **TanStack Query**
- **Axios**

### Database
- **PostgreSQL 15**
- **Docker Compose**

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Frontend serving & reverse proxy

---

## Docker Deployment

### Yêu cầu

- Docker Desktop (Windows/Mac/Linux)
- Docker Compose

### Khởi động nhanh

```powershell
# Di chuyển đến thư mục project
cd d:\AI-Agent-Customer-Service

# Build và chạy tất cả services
docker-compose up -d --build

# Xem logs
docker-compose logs -f

# Hoặc chạy background
docker-compose up -d
```

### Các lệnh Docker thường dùng

```powershell
# Khởi động services
docker-compose up -d

# Dừng services
docker-compose down

# Xem trạng thái
docker-compose ps

# Xem logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Rebuild không cache
docker-compose build --no-cache

# Reset hoàn toàn (xóa data)
docker-compose down -v
docker-compose up -d --build

# Restart một service
docker-compose restart backend
```

### Ports

| Service | Port | Mô tả |
|---------|------|--------|
| Frontend | http://localhost:3000 | Web UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger Documentation |
| PostgreSQL | localhost:5432 | Database |

### Seed Data

Sau khi khởi động lần đầu, chạy seed data:

```powershell
docker-compose exec backend python seed_data.py
```

---

## Development Local

### Yêu cầu

- Node.js 18+
- Python 3.11+
- Docker Desktop (cho PostgreSQL)

### 1. Khởi động PostgreSQL

```powershell
docker-compose up -d postgres
```

### 2. Backend

```powershell
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt
.\venv\Scripts\Activate

# Cài đặt dependencies
pip install -r requirements.txt

# Copy .env
copy .env.example .env

# Chạy seed data
python seed_data.py

# Khởi động
uvicorn main:app --reload --port 8000
```

Backend chạy tại: http://localhost:8000

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend chạy tại: http://localhost:5173

---

## Tài khoản Demo

| Vai trò | Email | Mật khẩu |
|---------|-------|----------|
| **Owner** | owner@hienhuu.vn | Owner@123 |
| **Customer** | customer@example.com | Customer@123 |

### Dữ liệu mẫu đã có

- 5 chuyến xe (Hà Nội ↔ Tà Xùa)
- 3 khách hàng
- 4 bookings (2 confirmed, 2 pending)
- 2 payments (paid)
- 2 complaints (open)
- 1 refund request (waiting approval)

---

## API Endpoints

### Authentication

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/api/auth/register` | Đăng ký tài khoản |
| POST | `/api/auth/login` | Đăng nhập |
| GET | `/api/auth/me` | Lấy thông tin user hiện tại |

### Trips

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/trips` | Lấy danh sách chuyến xe |
| GET | `/api/trips/{id}` | Chi tiết chuyến xe |
| POST | `/api/trips` | Tạo chuyến xe (owner) |
| PUT | `/api/trips/{id}` | Cập nhật chuyến xe (owner) |
| DELETE | `/api/trips/{id}` | Xóa chuyến xe (owner) |

### Bookings

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/bookings` | Danh sách booking của tôi |
| GET | `/api/bookings/all` | Tất cả bookings (owner) |
| GET | `/api/bookings/{id}` | Chi tiết booking |
| POST | `/api/bookings` | Tạo booking mới |
| PATCH | `/api/bookings/{id}/cancel` | Hủy booking |

### Payments

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/payments/{id}` | Chi tiết payment |
| POST | `/api/payments/{id}/pay` | Mô phỏng thanh toán |

### Complaints

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/complaints` | Danh sách khiếu nại của tôi |
| GET | `/api/complaints/all` | Tất cả khiếu nại (owner) |
| GET | `/api/complaints/{id}` | Chi tiết khiếu nại |
| POST | `/api/complaints` | Tạo khiếu nại |
| PATCH | `/api/complaints/{id}` | Cập nhật khiếu nại (owner) |
| POST | `/api/complaints/{id}/resolve` | Giải quyết khiếu nại (owner) |

### Refunds

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/refunds` | Danh sách hoàn tiền của tôi |
| GET | `/api/refunds/pending` | Danh sách chờ duyệt (owner) |
| GET | `/api/refunds/all` | Tất cả refunds (owner) |
| GET | `/api/refunds/{id}` | Chi tiết refund |
| POST | `/api/refunds` | Tạo yêu cầu hoàn tiền |
| POST | `/api/refunds/{id}/approve` | Duyệt hoàn tiền (owner) |
| POST | `/api/refunds/{id}/reject` | Từ chối hoàn tiền (owner) |
| POST | `/api/refunds/{id}/mark-refunded` | Đánh dấu đã hoàn tiền (owner) |

### Dashboard & Audit

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/dashboard/stats` | Thống kê dashboard (owner) |
| GET | `/api/audit-logs` | Nhật ký audit (owner) |

---

## Luồng Demo chính

### 1. Luồng đặt vé (Customer)

```
1. Đăng nhập với customer@example.com
2. Vào "Tìm chuyến"
3. Tìm "Hà Nội → Tà Xùa"
4. Chọn chuyến → Nhập số ghế
5. Xác nhận đặt vé
6. Thanh toán (mô phỏng)
7. Xem booking đã xác nhận
```

### 2. Luồng khiếu nại & hoàn tiền (Customer)

```
1. Đăng nhập với customer@example.com
2. Vào "Khiếu nại" → Tạo khiếu nại
3. Vào "Hoàn tiền" → Tạo yêu cầu hoàn tiền
4. Điền thông tin tài khoản
5. Gửi yêu cầu
```

### 3. Luồng duyệt hoàn tiền (Owner)

```
1. Đăng nhập với owner@hienhuu.vn
2. Vào "Duyệt hoàn tiền"
3. Xem yêu cầu đang chờ
4. Nhấn "Phê duyệt"
5. Nhấn "Đánh dấu đã hoàn tiền"
6. Kiểm tra "Audit Log"
```

### 4. Quản lý chuyến xe (Owner)

```
1. Đăng nhập với owner@hienhuu.vn
2. Vào "Chuyến xe"
3. Thêm chuyến xe mới
4. Sửa thông tin chuyến
5. Xóa chuyến xe không cần
```

---

## AI-Ready Architecture

Mặc dù chưa tích hợp AI, backend được thiết kế để dễ dàng mở rộng với AI Agent:

### Service Layer cho AI Tools

```python
# TripService methods cho AI
- search_trips(origin, destination, date)
- check_available_seats(trip_id)
- get_trip_detail(trip_id)

# BookingService methods cho AI
- create_booking(user_id, trip_id, seat_count)
- get_booking(booking_id)
- check_booking_status(booking_id)

# PaymentService methods cho AI
- create_payment(booking_id)
- check_payment_status(payment_id)

# ComplaintService methods cho AI
- create_complaint(customer_id, booking_id, type, description)
- get_complaints_by_booking(booking_id)
- check_refund_eligibility(booking_id)

# RefundService methods cho AI
- create_refund_request(complaint_id, booking_id, amount, bank_info)
- get_pending_refunds()
- submit_for_approval(refund_id)

# AuditService methods cho AI
- log_action(actor, action, entity, entity_id, metadata)
- get_audit_trail(entity_type, entity_id)
```

### Design Patterns

1. **Service Layer Pattern** - Tách biệt business logic khỏi API routes
2. **Repository Pattern** - Truy xuất data qua service
3. **Dependency Injection** - FastAPI dependency system
4. **Audit Trail** - Mọi action đều được log

---

## Roadmap

### Phase 1 (MVP - Hiện tại) ✅
- [x] Backend REST API
- [x] Frontend Customer/Owner Dashboard
- [x] Database với seed data
- [x] Authentication & Authorization
- [x] CRUD operations
- [x] Workflow: Booking → Payment → Complaint → Refund
- [x] Docker deployment

### Phase 2 - AI Integration
- [ ] Tích hợp LangGraph
- [ ] Chief Agent cho intent detection
- [ ] Booking & Payment Agent
- [ ] Complaint Agent
- [ ] RAG cho knowledge base

### Phase 3 - Enhancement
- [ ] Real-time notifications
- [ ] Email/SMS integration
- [ ] Payment gateway thật
- [ ] Mobile app

---

## License

MIT
