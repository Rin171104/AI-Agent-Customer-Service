# AI Agent Platform for Hiền Hựu Bus Customer Service & Operations

> Hệ thống AI Agent đa tác tử cho chăm sóc khách hàng, đặt vé & xử lý khiếu nại / Multi-Agent AI System for Customer Service, Ticket Booking & Complaint Handling

---

## Mục lục / Table of Contents

1. [Tổng quan](#tổng-quan)
2. [Vấn đề](#vấn-đề)
3. [Tại sao Multi-Agent?](#tại-sao-multi-agent)
4. [Luồng sản phẩm](#luồng-sản-phẩm)
5. [Kiến trúc](#kiến-trúc)
6. [Các Agent](#các-agent)
7. [Agent vs Tools](#agent-vs-tools)
8. [Khả năng dùng chung](#khả-năng-dùng-chung)
9. [Luồng nghiệp vụ](#luồng-nghiệp-vụ)
10. [Business State](#business-state)
11. [Tính năng chính](#tính-năng-chính)
12. [Tech Stack](#tech-stack)
13. [Demo](#demo)
14. [Cấu trúc dự án](#cấu-trúc-dự-án)
15. [API](#api)
16. [Cấu hình](#cấu-hình)
17. [Quick Start](#quick-start)
18. [Lộ trình](#lộ-trình)
19. [Tài liệu](#tài-liệu)
20. [License](#license)

---

## Tổng quan / Overview

**AI Multi-Agent Operations Assistant** cho Nhà xe Hiền Hựu.

Hệ thống tự động hóa hoạt động CSKH và vận hành cho doanh nghiệp một người:

| Nghiệp vụ / Domain | Mô tả / Description |
|---------------------|----------------------|
| **Chăm sóc khách hàng / Customer Service** | Tra cứu thông tin nhà xe, lịch trình, dịch vụ |
| **Thông tin chuyến / Trip Information** | Tìm chuyến, kiểm tra ghế |
| **Đặt vé / Ticket Booking** | Đặt vé, giữ ghế, xác nhận |
| **Thanh toán / Payment** | Thanh toán, theo dõi trạng thái |
| **Xử lý khiếu nại / Complaint Handling** | Tiếp nhận, phân loại, xử lý khiếu nại |

### Đây KHÔNG phải là chatbot đơn thuần / What This Is NOT

Đây **không chỉ là chatbot trả lời câu hỏi**:

```
Yêu cầu khách hàng / Customer Request
        ↓
Chief Agent (Điều phối viên)
        ↓
Agent chuyên biệt / Specialist Agent
        ↓
Tools / RAG / Database
        ↓
Xác thực / Validation
        ↓
Phê duyệt Human (nếu cần) / Human Approval (when required)
        ↓
Hành động nghiệp vụ / Business Action
        ↓
Cập nhật State
```

Hệ thống thực hiện **luồng nghiệp vụ thực tế** — không chỉ sinh text.

### 4 Tiêu chí chính / Four Key Criteria

| # | Tiêu chí | Criteria | Mô tả / Description |
|---|----------|----------|----------------------|
| 1 | Bot làm việc thật | Bot works for real | Multi-step, gọi tool, quản lý state |
| 2 | Phối hợp | Coordination | Nhiều agent handoff kèm context |
| 3 | Quản trị mặc định | Default governance | Action rủi ro cần duyệt + audit |
| 4 | Đích đến | Complete journey | Chat → Handoff → Work → Approve → Audit |

---

## Vấn đề / Problem

### Pain Points

Với mô hình doanh nghiệp một người, chủ nhà xe phải đồng thời:

| Nhóm / Category | Công việc / Tasks |
|-----------------|-------------------|
| **CSKH / Customer Service** | Tư vấn, tra cứu lịch/chuyến, giá, ghế |
| **Đặt vé / Booking** | Đặt vé, theo dõi thanh toán, tra cứu booking |
| **Khiếu nại / Complaints** | Xử lý khiếu nại, yêu cầu hoàn tiền |

Công việc lặp lại chiếm thời gian, trong khi nghiệp vụ quan trọng cần chủ doanh nghiệp quyết định.

### Giải pháp / Solution

```
Công việc thường xuyên          Nghiệp vụ rủi ro
        ↓                              ↓
       AI                              AI
        ↓                              ↓
Tự động xử lý              Chủ nhà xe kiểm soát
```

---

## Tại sao Multi-Agent? / Why Multi-Agent?

| Tiêu chí / Concern | Agent đơn lẻ / Single Agent | Multi-Agent |
|---------------------|------------------------------|-------------|
| **Tách biệt domain / Domain separation** | Logic lẫn lộn | Agent chuyên biệt theo domain |
| **Đặt vé vs Khiếu nại / Booking vs Complaint** | Luật chồng chéo | Ranh giới rõ ràng |
| **Thanh toán / Payment flow** | Lẫn với intent khác | Agent downstream riêng |
| **Mở rộng / Scalability** | Phức tạp khi thêm feature | Thêm agent không cần viết lại |
| **Bảo trì / Maintainability** | Prompt phức tạp | Agent có trách nhiệm riêng |
| **Kiểm soát / Controllability** | Khó audit | Delegation & validation rõ ràng |

**Mục tiêu không phải tạo nhiều agent, mà tách biệt trách nhiệm nghiệp vụ khác nhau.**

---

## Luồng sản phẩm / Product Flow

```
Hiểu / Understand
    ↓
Lập kế hoạch / Plan
    ↓
Ủy thác / Delegate
    ↓
Thực thi / Execute
    ↓
Xác thực / Validate
    ↓
Phê duyệt Human / Human Approval (nếu cần)
    ↓
Hành động / Act
    ↓
Cập nhật State
```

---

## Kiến trúc / Architecture

```mermaid
flowchart TD
    U[Khách hàng / Customer] --> C[Chief Agent]

    C --> B[Booking & Payment Agent]
    C --> CO[Complaint Agent]

    B --> BT[Booking Tools]
    CO --> CT[Complaint Tools]

    B --> DB[(PostgreSQL)]
    CO --> DB

    CO --> R[RAG / Knowledge Base<br/>Thông tin Hiền Hựu]

    C --> V[Xác thực / Validation]

    V --> H{Rủi ro cao? / Risk Check?}

    H -->|Không / No| A[Tự động / Auto]
    H -->|Có / Yes| HITL[Chủ nhà xe duyệt / Owner Approval]

    A --> S[State cập nhật / State Updated]
    HITL --> S
```

---

## Các Agent / Agents

### Chief Agent

**Điều phối viên / Orchestrator** — điều phối toàn bộ workflow.

| Trách nhiệm / Responsibility | Mô tả / Description |
|-------------------------------|------------------------|
| Hiểu yêu cầu / Understand request | Tiếp nhận và parse input |
| Phát hiện intent / Detect intent | Xác định booking, complaint, payment, FAQ |
| Ủy thác task / Delegate task | Route đến Agent phù hợp |
| Điều phối workflow / Coordinate | Quản lý các bước |
| Xác thực kết quả / Validate | Kiểm tra output từ specialist |
| Trigger HITL | Kích hoạt human approval khi cần |

### Booking & Payment Agent

**Domain: Đặt vé & Thanh toán Hiền Hựu**

| Khả năng / Capability | Mô tả / Description |
|------------------------|----------------------|
| Tìm chuyến / Search trips | Tìm chuyến theo tuyến và ngày |
| Kiểm tra ghế / Check seats | Hiển thị ghế trống |
| Thu thập thông tin / Collect info | Thu thập thông tin khách |
| Tạo booking / Create booking | Tạo booking chờ xác nhận |
| Xử lý thanh toán / Process payment | Workflow thanh toán |
| Xác nhận booking / Confirm booking | Cập nhật trạng thái |

**Tools:**

```text
search_trip()          # Tìm chuyến
get_trip_detail()      # Chi tiết chuyến
check_available_seats() # Kiểm tra ghế
hold_seat()            # Giữ ghế
create_booking()        # Tạo booking
get_booking()          # Lấy thông tin booking
create_payment()       # Tạo thanh toán
check_payment_status()  # Kiểm tra thanh toán
```

### Complaint Agent

**Domain: Xử lý khiếu nại / Customer Complaints**

| Khả năng / Capability | Mô tả / Description |
|------------------------|----------------------|
| Tiếp nhận khiếu nại / Receive | Tiếp nhận và phân loại |
| Tra cứu booking / Retrieve | Lấy thông tin booking liên quan |
| Phân loại type / Classify type | WRONG_SEAT, LATE, DRIVER, LOST_ITEM, PAYMENT, BOOKING_ERROR, REFUND, OTHER |
| Đánh giá mức độ / Assess severity | LOW, MEDIUM, HIGH |
| Đề xuất giải pháp / Recommend | Đề xuất hướng xử lý |
| Escalate | Chuyển chủ nhà xe khi cần |

---

## Agent vs Tools

### Agents

Chịu trách nhiệm cho:
- **Reasoning** — suy luận và quyết định
- **Delegation** — ủy thác và điều phối
- **Workflow decisions** — quyết định luồng xử lý
- **Domain-specific** — xử lý nghiệp vụ riêng

### Tools

Chịu trách nhiệm cho các thao tác **xác định (deterministic)**:

| Domain | Operations |
|--------|------------|
| **Đặt vé / Booking** | `search_trip`, `check_seat`, `hold_seat`, `create_booking` |
| **Thanh toán / Payment** | `create_payment`, `check_payment`, `confirm_payment` |
| **Khiếu nại / Complaint** | `create_complaint`, `get_complaint`, `update_complaint` |

Tools thực hiện action; chúng không suy luận.

---

## Khả năng dùng chung / Shared Capabilities

### RAG / Knowledge Base

**RAG là capability dùng chung, KHÔNG PHẢI agent.**

Dùng để truy xuất thông tin được phê duyệt:

| Loại thông tin / Information Type | Ví dụ / Example |
|----------------------------------|-----------------|
| Loại xe / Vehicle types | Limousine, Cabin |
| Khu vực dịch vụ / Service areas | Tuyến Hà Nội ↔ Tà Xùa |
| Điểm đón/trả / Pickup/drop-off | Điểm đón, điểm trả |
| Chính sách / Policies | Chính sách hoàn, hủy |
| FAQ | Câu hỏi thường gặp |

**Quan trọng:** RAG truy xuất knowledge; không thay thế tools giao dịch.

```
"Câu hỏi về lịch trình?"
→ Knowledge Base / Trip Data Tool

"Đặt 2 vé."
→ Booking Agent + Tools
```

### Shared State

Agents chia sẻ context trong suốt workflow:

```json
{
  "user_id": "...",
  "intent": "booking",
  "origin": "Hà Nội / Hanoi",
  "destination": "Tà Xùa / Ta Xua",
  "travel_date": "2026-09-20",
  "quantity": 2,
  "trip_id": "...",
  "customer_name": "...",
  "phone": "...",
  "booking_id": "...",
  "booking_status": "PENDING_PAYMENT",
  "payment_status": "UNPAID",
  "requires_human_approval": false
}
```

### Human-in-the-Loop

**HITL là cổng kiểm soát có điều kiện** cho các action nhạy cảm.

| AI tự động / AI can do | Cần duyệt / Owner must approve |
|-------------------------|-------------------------------|
| FAQ, tra cứu thông tin | Hoàn tiền / Refunds |
| Kiểm tra chuyến, ghế | Khiếu nại nghiêm trọng |
| Tạo booking | Request ngoài policy |
| Phân loại khiếu nại | Action tài chính |

---

## Luồng nghiệp vụ / Core Workflows

### Luồng đặt vé / Booking Workflow

```mermaid
flowchart LR
    A[Khách / Customer] -->|Yêu cầu / Request| B[Chief]
    B -->|Ủy thác / Delegate| C[Booking Agent]
    C --> D[Tìm chuyến / Search Trip]
    D --> E[Kiểm tra ghế / Check Seats]
    E --> F[Hiển thị options]
    F --> A
    A -->|Chọn / Select| G[Thu thập info]
    G --> H[Tạo Booking]
    H --> I[Khách xác nhận / Confirm]
    I --> J[Thanh toán / Payment]
    J --> K{Kiểm tra / Check}
    K -->|Thành công / Success| L[Xác nhận / Confirm]
    K -->|Thất bại / Fail| M[Thử lại / Retry]
    L --> N[State cập nhật]
```

### Luồng khiếu nại / Complaint Workflow

```mermaid
flowchart TD
    A[Khách] -->|Khiếu nại| B[Chief]
    B -->|Ủy thác| C[Complaint Agent]
    C --> D[Lấy Booking]
    D --> E[Phân loại]
    E --> F{Đánh giá mức độ}
    F -->|Thấp / Low| G[Tự xử lý]
    F -->|Cao / High| H[Chủ nhà xe duyệt]
    G --> I[Cập nhật State]
    H --> J{Duyệt?}
    J -->|Có| K[Thực thi]
    J -->|Không| L[Từ chối]
    K --> I
    I --> M[Thông báo]
```

### Luồng hoàn tiền / Refund Flow

```
Khách yêu cầu hoàn tiền
        ↓
Complaint Agent
        ↓
get_booking() + RAG: refund_policy
        ↓
Kiểm tra điều kiện
        ↓
Tạo Refund Request
        ↓
⚠️ Human Approval
        ↓
Chủ nhà xe xem xét
        ↓
Thực hiện hoàn tiền (bên ngoài)
        ↓
Cập nhật Database: REFUNDED
        ↓
Audit Log
        ↓
Thông báo khách
```

**Lưu ý:** AI **không trực tiếp chuyển tiền**. AI tạo, theo dõi và cập nhật request; chủ nhà xe thực hiện giao dịch thực tế.

---

## Business State

Agents vận hành trên business state thông qua các tools được kiểm soát.

| Entity | Mô tả |
|--------|--------|
| **Customer** | Thông tin khách |
| **Route** | Tuyến đi (Hà Nội ↔ Tà Xùa) |
| **Trip** | Chuyến xe với giờ, loại xe |
| **Vehicle** | Loại xe (Limousine, Cabin) |
| **Seat** | Ghế với trạng thái |
| **Booking** | Bản ghi đặt vé |
| **Payment** | Bản ghi thanh toán |
| **Complaint** | Bản ghi khiếu nại |

---

## Tính năng chính / Key Features

| Tính năng / Feature | Mô tả / Description |
|---------------------|----------------------|
| Intent Detection | Định tuyến request đến workflow phù hợp |
| Multi-Agent Handoff | Ủy thác cho specialist kèm context |
| Tool Calling | Thực thi nghiệp vụ |
| RAG | Truy xuất thông tin Hiền Hựu |
| HITL | Kiểm soát action nhạy cảm |
| Shared State | Duy trì context xuyên suốt workflow |
| Audit Log | Theo dõi execution |

---

## Tech Stack

### Backend

| Component | Technology |
|-----------|------------|
| Ngôn ngữ / Language | Python 3.11+ |
| Framework | FastAPI |
| Agent Framework | LangGraph |

### AI

| Component | Technology |
|-----------|------------|
| LLM | OpenAI GPT-4 / Anthropic Claude |
| Embeddings | OpenAI Embeddings |
| RAG | Semantic search với pgvector |

### Database

| Component | Technology |
|-----------|------------|
| Relational | PostgreSQL 15+ |
| Vector | pgvector |

### Frontend

| Component | Technology |
|-----------|------------|
| Runtime | Node.js |
| Framework | Express.js / React |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Container | Docker |
| Database | Docker Compose |

---

## Demo

```
Khách hàng:
"Tôi muốn đặt 2 vé Hà Nội đi Tà Xùa."

Chief Agent:
→ Phát hiện: booking intent
→ Entities: origin=Hà Nội, destination=Tà Xùa, quantity=2
→ Ủy thác cho Booking Agent

Booking Agent:
→ search_trip(origin="Hà Nội", destination="Tà Xùa")
→ check_available_seats(trip_id="...")
→ Kết quả: chuyến 20:00, ghế A05, A06 trống

Chief Agent:
→ "Có chuyến 20:00 với ghế A05, A06. Đặt không?"

Khách:
"Đặt."

Booking Agent:
→ hold_seat(trip_id="...", seats=["A05", "A06"])
→ create_booking(customer_info={...})
→ Kết quả: booking_id="BK001", status=BOOKING_DRAFT

Chief Agent:
→ "Booking BK001 đã tạo. Chuyển thanh toán?"

Khách:
"Xác nhận."

Booking Agent:
→ create_payment(booking_id="BK001", amount=...)
→ check_payment_status(booking_id="...")
→ Kết quả: PAID

Chief Agent:
→ "Thanh toán thành công. Booking BK001 xác nhận!"

Final State:
→ booking_id: BK001
→ booking_status: CONFIRMED
→ payment_status: PAID
→ seats: A05, A06
```

---

## Cấu trúc dự án / Project Structure

```
ai-agent-customer-service/
│
├── backend/
│   ├── src/
│   │   ├── agent/
│   │   │   ├── chief.py           # Chief Agent
│   │   │   ├── booking.py         # Booking & Payment Agent
│   │   │   ├── complaint.py       # Complaint Agent
│   │   │   ├── state.py           # Shared state
│   │   │   └── executor.py        # Agent executor
│   │   │
│   │   ├── tools/
│   │   │   ├── booking_tools.py   # Booking operations
│   │   │   ├── payment_tools.py   # Payment operations
│   │   │   ├── complaint_tools.py # Complaint operations
│   │   │   └── search.py          # RAG search
│   │   │
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── utils/
│   │   └── api/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   └── services/
│   ├── package.json
│   └── tsconfig.json
│
├── data/
│   └── knowledge-base/
│       └── README.md        # Placeholder - cập nhật dữ liệu thực
│
├── docs/
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## API

| Endpoint | Method | Mô tả / Description |
|----------|--------|---------------------|
| `/api/chat` | POST | Gửi tin nhắn, nhận phản hồi từ Agent |
| `/api/bookings` | GET, POST | Liệt kê hoặc tạo booking |
| `/api/bookings/{id}` | GET, PUT | Lấy hoặc cập nhật booking |
| `/api/trips` | GET | Tìm chuyến theo tuyến và ngày |
| `/api/payments` | POST | Tạo thanh toán |
| `/api/payments/{id}/confirm` | POST | Xác nhận thanh toán |
| `/api/complaints` | GET, POST | Liệt kê hoặc tạo khiếu nại |
| `/api/admin/pending-approvals` | GET | Lấy danh sách duyệt |
| `/api/admin/approvals/{id}` | POST | Xử lý duyệt |

---

## Cấu hình / Configuration

Environment variables (xem `backend/.env.example`):

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_agent_cs
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
SECRET_KEY=your-secret-key
DEBUG=true
```

---

## Quick Start

### Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate   # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình environment
cp .env.example .env

# Khởi động server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database (Docker)

```bash
docker-compose up -d
```

---

## Lộ trình / Roadmap

### Phase 1 — MVP

- [ ] Core Agent architecture (Chief + Specialist Agents)
- [ ] Luồng đặt vé (search → book → pay → confirm)
- [ ] Luồng khiếu nại (receive → classify → resolve)
- [ ] Basic RAG cho thông tin Hiền Hựu
- [ ] Cơ chế Human-in-the-Loop
- [ ] Audit Log

### Phase 2 — Customer Service

- [ ] Hỗ trợ đa kênh (Web, Zalo, Facebook)
- [ ] Conversation memory
- [ ] Customer history

### Phase 3 — Operations

- [ ] Fleet/Trip Management
- [ ] Revenue Analytics
- [ ] Reporting Dashboard

---

## Tài liệu / Documentation

- [PRD](PRD%20%E2%80%94%20AI%20Agent%20Customer%20Service%20&%20Ticket%20Booking%20Platform.md) — Product Requirements chi tiết

---

## Data Accuracy Notice

> Schedule, pricing, seat availability and pickup/drop-off information may change over time. The AI system should retrieve transactional information from the current business data source or tools rather than relying solely on static knowledge.

> Lịch trình, giá vé, số ghế trống và thông tin điểm đón/trả có thể thay đổi theo thời gian. Hệ thống AI nên truy xuất thông tin giao dịch từ nguồn dữ liệu hiện tại thay vì chỉ dựa vào knowledge base tĩnh.

---

## License

MIT
