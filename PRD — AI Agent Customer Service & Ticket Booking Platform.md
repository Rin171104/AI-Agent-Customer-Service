# PRD — AI Agent Multi-Agent Operations Assistant cho Nhà xe Hiền Hựu

## 1. Tổng quan sản phẩm

### 1.1. Tên sản phẩm

**AI Multi-Agent Operations Assistant cho Nhà xe Hiền Hựu**

### 1.2. Định vị

Dự án xây dựng một hệ thống **AI Operations Assistant** giúp chủ nhà xe tự động hóa phần lớn hoạt động CSKH và vận hành hằng ngày.

AI đóng vai trò như một **đội ngũ vận hành ảo**: tiếp nhận yêu cầu, tự thực hiện nhiều bước, gọi công cụ, phối hợp giữa các agent và chỉ chuyển cho chủ nhà xe những quyết định có rủi ro hoặc cần quyền con người.

### 1.3. Domain

- **Nhà xe:** Hiền Hựu
- **Tuyến chính:** Hà Nội ↔ Tà Xùa
- **Loại xe:** Limousine, Cabin

### 1.4. Mô tả

Hệ thống AI Agent cho Nhà xe Hiền Hựu tự động hóa hoạt động **chăm sóc khách hàng, đặt vé, thanh toán và xử lý khiếu nại**.

Thay vì xây dựng một chatbot chỉ trả lời câu hỏi, hệ thống sử dụng kiến trúc **Multi-Agent**, trong đó **Chief Agent** đóng vai trò điều phối trung tâm, tự động phân tích yêu cầu và giao nhiệm vụ cho các Specialist Agent.

Các Specialist Agent chính:

- **Booking & Payment Agent:** xử lý nghiệp vụ đặt vé và thanh toán.
- **Complaint Agent:** xử lý khiếu nại.

Các Agent có thể sử dụng những capability chung như:

- RAG / Knowledge Base.
- Database.
- Booking Tools.
- Payment Tools.
- Customer/Trip Management APIs.

Các trường hợp có rủi ro hoặc vượt quá phạm vi xử lý của AI sẽ được chuyển cho chủ nhà xe thông qua cơ chế **Human-in-the-Loop**.

### 1.5. Phạm vi MVP

- Tư vấn và tra cứu thông tin.
- Đặt vé và thanh toán.
- Tra cứu booking.
- Tiếp nhận và xử lý khiếu nại.
- Tạo và theo dõi yêu cầu hoàn tiền.

---

## 2. Pain Point & Evidence

### 2.1. Pain Point

Với mô hình doanh nghiệp một người, chủ nhà xe có thể phải đồng thời xử lý:

- Tư vấn khách hàng.
- Kiểm tra lịch/chuyến.
- Kiểm tra số ghế.
- Đặt vé.
- Theo dõi thanh toán.
- Tra cứu booking.
- Xử lý khiếu nại.
- Kiểm tra yêu cầu hoàn tiền.

Các công việc lặp lại chiếm thời gian của chủ nhà xe, trong khi những nghiệp vụ quan trọng vẫn cần chủ doanh nghiệp trực tiếp quyết định.

### 2.2. Giải pháp

AI xử lý các công việc có thể chuẩn hóa và tự động hóa:

```
Công việc thường xuyên
        ↓
       AI
        ↓
Tự động xử lý

Nghiệp vụ rủi ro
        ↓
       AI
        ↓
  Chủ nhà xe
        ↓
Quyết định / thực hiện
```

### 2.3. Evidence

Dữ liệu công khai về nhà xe có thể khác nhau giữa các nguồn về lịch trình, giá hoặc dịch vụ. Vì vậy, hệ thống phân biệt:

- **Kiến thức tương đối ổn định → RAG**
- **Dữ liệu giao dịch/realtime → Tools + Database**

RAG không được sử dụng như nguồn dữ liệu realtime về số ghế, booking hoặc trạng thái thanh toán.

---

## 3. Product Vision

> **Xây dựng một AI Operating System cho hoạt động CSKH của nhà xe Hiền Hựu, trong đó nhiều AI Agent có thể tự phối hợp để xử lý một nghiệp vụ end-to-end, nhưng vẫn đảm bảo con người kiểm soát các quyết định quan trọng.**

### 3.1. Bốn tiêu chí chính

| # | Tiêu chí | Mô tả |
|---|-----------|--------|
| 1 | **Bot làm việc thật** | Nhận việc, tự chạy nhiều bước và gọi tool |
| 2 | **Phối hợp** | Nhiều agent phối hợp và handoff kèm context |
| 3 | **Quản trị mặc định** | Hành động rủi ro cần human approval và có audit log |
| 4 | **Đích đến** | Hero Flow hoàn chỉnh từ Chat → Handoff → Làm việc → Duyệt → Audit |

---

## 4. Target Users

### 4.1. Khách hàng

Khách hàng tương tác với AI để:

- Hỏi thông tin nhà xe.
- Hỏi lịch trình.
- Kiểm tra ghế.
- Đặt vé.
- Thanh toán.
- Tra cứu booking.
- Gửi khiếu nại.
- Yêu cầu hoàn tiền.

### 4.2. Chủ nhà xe

Chủ nhà xe sử dụng hệ thống để:

- Theo dõi booking.
- Theo dõi khiếu nại.
- Xem các yêu cầu cần xử lý.
- Duyệt các nghiệp vụ có rủi ro.
- Thực hiện hoàn tiền.
- Theo dõi audit log và lịch sử hoạt động của AI.

---

## 5. Agent Architecture

### 5.1. Kiến trúc tổng thể

```text
                    CUSTOMER
                       │
                       ▼
              ┌─────────────────┐
              │   Chief Agent   │
              │   Orchestrator  │
              └────────┬────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐       ┌─────────────────┐
│ Booking & Payment│       │ Complaint Agent │
│     Agent       │       │                 │
└────────┬─────────┘       └────────┬────────┘
         │                          │
         └───────────┬──────────────┘
                     ▼
           ┌────────────────────┐
           │  RAG / Tools / DB  │
           └──────────┬─────────┘
                     │
              Risk / Guardrail
                     │
            ┌────────┴────────┐
            ▼                 ▼
      Auto Response     ┌──────────────┐
            │           │ Chủ nhà xe  │
            │           │   Approval   │
            │           └──────┬───────┘
            │                  │
            └────────┬─────────┘
                     ▼
                  Audit Log
```

### 5.2. Chief Agent

**Vai trò:** Orchestrator của toàn hệ thống.

Chief Agent không trực tiếp thực hiện các nghiệp vụ như tạo booking hay thanh toán.

**Responsibilities:**

- Hiểu yêu cầu của khách.
- Xác định intent.
- Lập kế hoạch xử lý.
- Delegate task cho Specialist Agent.
- Truyền context giữa các bước.
- Theo dõi trạng thái.
- Validate kết quả.
- Quyết định trả lời tự động hoặc chuyển Human-in-the-loop.

**Flow:**

```
Understand
    ↓
Plan
    ↓
Route
    ↓
Delegate
    ↓
Observe
    ↓
Validate
    ↓
Respond / Escalate
```

### 5.3. Booking & Payment Agent

**Domain:** Hiền Hựu Ticket Booking & Payment

**Responsibilities:**

- Tìm chuyến.
- Xem chi tiết chuyến.
- Kiểm tra ghế.
- Giữ ghế.
- Tạo booking.
- Thu thập thông tin khách.
- Xác nhận booking.
- Theo dõi trạng thái thanh toán.

**Tools:**

```text
search_trip()
get_trip_detail()
check_available_seats()
hold_seat()
create_booking()
get_booking()
create_payment()
check_payment_status()
```

### 5.4. Complaint Agent

**Domain:** Customer Complaint Management

**Responsibilities:**

- Tiếp nhận khiếu nại.
- Phân loại vấn đề.
- Tra cứu booking.
- Tra cứu chính sách.
- Phân tích mức độ nghiêm trọng.
- Đề xuất hướng xử lý.
- Tạo complaint/refund request.
- Escalate cho chủ nhà xe khi cần.

**Complaint Types:**

| Code | Mô tả |
|------|--------|
| `WRONG_SEAT` | Sai ghế |
| `LATE_DEPARTURE` | Trễ giờ khởi hành |
| `DRIVER_BEHAVIOR` | Thái độ tài xế |
| `LOST_ITEM` | Mất đồ |
| `PAYMENT` | Vấn đề thanh toán |
| `BOOKING_ERROR` | Lỗi booking |
| `REFUND` | Yêu cầu hoàn tiền |
| `OTHER` | Khác |

---

## 6. Bot làm việc thật

Tiêu chí quan trọng của hệ thống là AI phải **thực sự thực hiện nghiệp vụ**, không chỉ sinh câu trả lời.

Ví dụ khách yêu cầu:

> "Đặt 2 vé Hà Nội đi Tà Xùa tối nay."

AI thực hiện nhiều bước:

```
Customer
   ↓
Chief Agent
   ↓
Booking & Payment Agent
   ↓
search_trip()
   ↓
check_available_seats()
   ↓
collect_customer_info()
   ↓
create_booking()
   ↓
Customer Confirmation
   ↓
Payment
   ↓
check_payment_status()
   ↓
Booking Confirmed
```

**Điểm thể hiện:**

- Multi-step reasoning
- Tool calling
- State management
- Business data access
- End-to-end task execution

---

## 7. Phối hợp & Handoff

Các agent không hoạt động độc lập mà phối hợp thông qua **handoff kèm context**.

**Ví dụ booking:**

```
Customer
   ↓
Chief Agent
   ↓ handoff + context
Booking & Payment Agent
   ↓
Hoàn thành booking
   ↓
Chief Agent
   ↓
Customer
```

**Context truyền giữa các agent:**

```json
{
  "user_id": "...",
  "intent": "booking",
  "origin": "Hà Nội",
  "destination": "Tà Xùa",
  "travel_date": "2026-09-20",
  "trip_id": "...",
  "customer_info": {...},
  "booking_id": "...",
  "payment_status": "...",
  "complaint_id": "...",
  "requires_human": false
}
```

**Ví dụ khiếu nại có refund:**

```
Customer
   ↓
Chief Agent
   ↓
Complaint Agent
   ↓
Phát hiện yêu cầu Refund
   ↓
Tạo Refund Request
   ↓
Chief Agent
   ↓
Human-in-the-loop
```

Mục tiêu là đảm bảo agent tiếp theo nhận được đủ thông tin để tiếp tục workflow mà không cần khách hàng lặp lại toàn bộ yêu cầu.

---

## 8. RAG, Tools và Database

Hệ thống phân tách rõ giữa **knowledge** và **business data**.

### 8.1. RAG

Sử dụng cho:

- Thông tin nhà xe Hiền Hựu.
- Thông tin tuyến Hà Nội ↔ Tà Xùa.
- Dịch vụ (Limousine, Cabin).
- FAQ.
- Chính sách đặt/hủy/hoàn vé.
- Điểm đón/trả.

### 8.2. Tools + Database

Sử dụng cho:

- Chuyến hiện tại.
- Số ghế còn lại.
- Booking.
- Customer.
- Payment.
- Complaint.
- Refund request.

### 8.3. Nguyên tắc

> **RAG trả lời "nhà xe quy định/cung cấp gì".**

> **Tool + Database trả lời "hiện tại hệ thống đang có gì".**

**Ví dụ:**

```text
"Chính sách hoàn vé là gì?"
        → RAG

"Chuyến tối nay còn bao nhiêu ghế?"
        → Tool → Database

"Booking của tôi đang ở trạng thái nào?"
        → Tool → Database
```

---

## 9. Quản trị mặc định & Human-in-the-Loop

> **AI có thể tự động xử lý công việc, nhưng hành động có rủi ro phải có human control.**

### 9.1. AI có thể tự động xử lý

- FAQ.
- Tra cứu thông tin.
- Kiểm tra chuyến.
- Kiểm tra ghế.
- Tạo booking.
- Tra cứu payment status.
- Tiếp nhận và phân loại khiếu nại.

### 9.2. Cần chủ nhà xe kiểm soát

- Hoàn tiền.
- Tranh chấp.
- Khiếu nại nghiêm trọng.
- Yêu cầu ngoài chính sách.
- Các hành động có tác động tài chính.
- Trường hợp AI không đủ thông tin/confidence.

### 9.3. Refund Flow

```
Khách yêu cầu hoàn tiền
          ↓
Complaint Agent
          ↓
get_booking()
          ↓
RAG: refund_policy
          ↓
Kiểm tra điều kiện
          ↓
Thu thập thông tin ngân hàng
          ↓
Create Refund Request
          ↓
⚠️ HUMAN APPROVAL
          ↓
Chủ nhà xe kiểm tra
          ↓
Chủ nhà xe thực hiện refund
          ↓
Xác nhận REFUNDED
          ↓
Database cập nhật
          ↓
AI thông báo khách
```

**Lưu ý:** AI **không trực tiếp chuyển tiền**. AI tạo, theo dõi và cập nhật yêu cầu; chủ nhà xe thực hiện giao dịch thực tế.

---

## 10. Audit Log

Mọi hành động quan trọng của Agent cần có trace/audit log.

### 10.1. Thông tin cần lưu

```text
timestamp
user_id
agent
action
tool
input
output
booking_id
request_id
approval_required
human_approved
result
```

### 10.2. Ví dụ

```text
Agent: Complaint Agent
Action: CREATE_REFUND_REQUEST
Booking: BK00125
Amount: 300000
Approval: REQUIRED
Approved by: Business Owner
Result: REFUNDED
Timestamp: ...
```

### 10.3. Mục đích

- Theo dõi AI đã làm gì.
- Debug workflow.
- Kiểm tra các quyết định.
- Truy vết nghiệp vụ.
- Tăng khả năng kiểm soát hệ thống.

---

## 11. Hero Flow

Hero Flow thể hiện đầy đủ tiêu chí:

> **Chat → Handoff → Làm việc → Duyệt → Audit**

### 11.1. Hero Flow: Xử lý yêu cầu hoàn tiền

```
CUSTOMER
"Tôi muốn hoàn tiền vé này"
        ↓
CHIEF AGENT
        ↓
COMPLAINT AGENT
        ↓
get_booking()
        ↓
RAG: Refund Policy
        ↓
Kiểm tra điều kiện
        ↓
Create Refund Request
        ↓
⚠️ Handoff to Human
        ↓
CHỦ NHÀ XE
        ↓
Duyệt / từ chối
        ↓
Thực hiện refund nếu được duyệt
        ↓
Update Database
        ↓
Audit Log
        ↓
AI thông báo CUSTOMER
```

### 11.2. Bảng tiêu chí

| Tiêu chí | Cách đáp ứng |
|-----------|---------------|
| Bot làm việc thật | Agent gọi Tool + RAG + DB và thực hiện nhiều bước |
| Phối hợp | Chief Agent → Complaint Agent → Human |
| Handoff | Truyền booking/context giữa các bước |
| Quản trị | Human approval trước hành động rủi ro |
| Audit | Ghi lại toàn bộ action và kết quả |
| Đích đến | Chat → Handoff → Work → Approve → Audit |

---

## 12. Core User Flows

### 12.1. Booking Flow

```
Customer
   ↓
Chief Agent
   ↓
Booking & Payment Agent
   ↓
Search Trip
   ↓
Check Seats
   ↓
Return Options
   ↓
Customer Selects Trip
   ↓
Collect Information
   ↓
Hold Seats
   ↓
Create Booking Draft
   ↓
Customer Confirmation
   ↓
Payment
   ↓
Check Payment Status
   ↓
Booking Confirmed
```

### 12.2. Complaint Flow

```
Customer
   ↓
Chief Agent
   ↓
Complaint Agent
   ↓
Retrieve Booking
   ↓
Classify Complaint Type
   ↓
Assess Severity
   ↓
Generate Resolution
   ↓
 ┌───────────────┐
 │ Low Risk      │ → AI xử lý
 │ High Risk     │ → Human Approval
 └───────────────┘
   ↓
Update Complaint State
```

### 12.3. Refund Flow

```
Customer requests refund
   ↓
Complaint Agent
   ↓
get_booking() + RAG: refund_policy
   ↓
Check conditions
   ↓
Create Refund Request
   ↓
⚠️ Human Approval
   ↓
Business Owner reviews
   ↓
Execute refund (external)
   ↓
Update Database: REFUNDED
   ↓
Audit Log
   ↓
Notify Customer
```

---

## 13. Example Conversations

### 13.1. Booking Conversation

**Customer:**

> "Tôi muốn đặt 2 vé Hà Nội đi Tà Xùa tối nay."

**Chief Agent:**

```json
{
  "intent": "booking",
  "origin": "Hà Nội",
  "destination": "Tà Xùa",
  "date": "2026-09-20",
  "quantity": 2
}
```

→ Delegate Booking & Payment Agent.

**Booking & Payment Agent:**

```text
search_trip(origin="Hà Nội", destination="Tà Xùa", date="2026-09-20")
check_available_seats(trip_id="...")
```

→ Kết quả: Chuyến 20:00, còn ghế A05, A06.

**Chief Agent:**

> "Chuyến 20:00 ngày 20/09 còn 2 ghế A05 và A06. Bạn có muốn đặt không?"

**Customer:**

> "Có."

**Booking & Payment Agent:**

```text
hold_seat(trip_id="...", seats=["A05", "A06"])
create_booking(customer_info={...})
```

→ Booking draft created.

**Chief Agent:**

→ Handoff Payment Agent.

**Payment Agent:**

```text
create_payment(booking_id="...", amount=...)
check_payment_status(booking_id="...")
```

→ Payment confirmed.

**Chief Agent:**

→ Booking CONFIRMED.

### 13.2. Complaint Conversation

**Customer:**

> "Tôi đã đặt vé nhưng tài xế không đón tôi ở điểm đã đăng ký."

**Chief Agent:**

→ Delegate Complaint Agent.

**Complaint Agent:**

```text
get_booking(booking_id="...")
Classify: WRONG_SEAT / PICKUP_ISSUE
Severity: MEDIUM
```

→ Create complaint ticket.

**Chief Agent:**

> "Tôi đã ghi nhận khiếu nại của bạn về việc không được đón đúng điểm. Đang xử lý..."

→ Kiểm tra policy → Đề xuất resolution.

→ Severity MEDIUM → Cần human approval.

**Chủ nhà xe:**

→ Approve refund/compensation.

**Complaint Agent:**

```text
update_complaint(complaint_id="...", status="RESOLVED", resolution={...})
```

→ Thông báo khách hàng.

---

## 14. State Management

Hệ thống cần duy trì shared state trong quá trình Agent phối hợp.

```json
{
  "user_id": "...",
  "intent": "booking",

  "origin": "Hà Nội",
  "destination": "Tà Xùa",
  "travel_date": "2026-09-20",
  "departure_time": "20:00",

  "quantity": 2,
  "trip_id": "...",

  "customer_name": "...",
  "phone": "...",
  "pickup_point": "...",

  "booking_id": "...",
  "total_amount": 500000,

  "booking_status": "PENDING_PAYMENT",
  "payment_status": "UNPAID",

  "requires_human": false
}
```

Shared state giúp các Agent không phải hỏi lại thông tin đã có.

---

## 15. Functional Requirements

| ID | Requirement | Mô tả |
|----|-------------|--------|
| FR-01 | Intent Detection | Xác định được các intent: booking, complaint, payment, FAQ, general |
| FR-02 | Agent Routing | Chief Agent route request tới Agent phù hợp |
| FR-03 | Multi-Agent Handoff | Hỗ trợ Agent handoff trong cùng workflow |
| FR-04 | Tool Calling | Agent gọi tool để thực hiện action |
| FR-05 | RAG | Agent truy xuất knowledge base khi cần |
| FR-06 | Human-in-the-Loop | Có cơ chế yêu cầu chủ nhà xe approval |
| FR-07 | State Management | Workflow duy trì state xuyên suốt |
| FR-08 | Audit / Trace | Lưu lại agent, task, tool, kết quả, handoff, approval, state change |

---

## 16. Non-Functional Requirements

### 16.1. Reliability

Không được tự ý xác nhận booking nếu chưa có ghế hoặc chưa đáp ứng điều kiện booking.

### 16.2. Safety

Các hành động có rủi ro phải có Human Approval.

### 16.3. Traceability

Mọi action của Agent phải có trace.

### 16.4. Data Accuracy

> Schedule, pricing, seat availability and pickup/drop-off information may change over time. The AI system should retrieve transactional information from the current business data source or tools rather than relying solely on static knowledge.

### 16.5. Scalability

Có thể bổ sung Agent mới mà không phải thay đổi toàn bộ hệ thống.

### 16.6. Maintainability

Agent, Tool và Knowledge Base phải được tách biệt.

---

## 17. Technical Architecture

```text
                         ┌───────────────┐
                         │   CUSTOMER    │
                         └───────┬───────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Chief Agent   │
                        │   Orchestrator  │
                        │   LangGraph     │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌──────────────────┐       ┌─────────────────┐
          │ Booking & Payment│       │ Complaint Agent │
          │      Agent       │       │                 │
          └────────┬─────────┘       └────────┬────────┘
                   │                          │
                   └───────────┬──────────────┘
                               ▼
                     ┌────────────────────┐
                     │   RAG / Tools / DB  │
                     │   - search_trip     │
                     │   - create_booking  │
                     │   - create_payment  │
                     │   - create_complaint│
                     │   - pgvector       │
                     └──────────┬─────────┘
                                │
                         Risk / Guardrail
                                │
                       ┌────────┴────────┐
                       ▼                 ▼
                 Auto Response     ┌──────────────┐
                       │           │ Chủ nhà xe  │
                       │           │   Approval   │
                       │           └──────┬───────┘
                       │                  │
                       └─────────┬────────┘
                                 ▼
                              Audit Log
```

### 17.1. Technology Stack

| Thành phần | Công nghệ |
|------------|-----------|
| Frontend | Node.js |
| Backend | Python + FastAPI |
| Agent Framework | LangGraph |
| LLM Orchestration | LangChain |
| RAG | Embedding + pgvector |
| Database | PostgreSQL |
| API | REST API |
| Business Data | Tools + PostgreSQL |
| Human-in-the-loop | Owner Dashboard |

---

## 18. MVP Scope

MVP tập trung vào một workflow hoàn chỉnh:

> **Customer → Booking → Payment → Confirmation**

và một workflow thứ hai:

> **Customer → Complaint → Human Approval**

### 18.1. MVP Agents

```text
1. Chief Agent (Orchestrator)
2. Booking & Payment Agent
3. Complaint Agent
```

### 18.2. MVP Capabilities

```text
RAG (Knowledge Base)
Database (PostgreSQL + pgvector)
Booking Tools
Payment Tools
Complaint Tools
Human-in-the-Loop
Agent Trace / Audit Log
```

---

## 19. Evaluation & Metrics

### 19.1. RAG

| Metric | Mô tả |
|--------|--------|
| **Recall@5** | Context liên quan có xuất hiện trong top-5 hay không |
| **Context Accuracy** | Context được retrieve có chính xác/phù hợp không |
| **Faithfulness** | Câu trả lời có bám vào context không |

### 19.2. Agent

| Metric | Mô tả |
|--------|--------|
| **Tool Calling Accuracy** | Agent có chọn và gọi đúng tool không |
| **Task Completion** | Workflow có hoàn thành đúng mục tiêu không |

### 19.3. Multi-Agent

| Metric | Mô tả |
|--------|--------|
| **Handoff Accuracy** | Agent có chuyển đúng workflow/agent không |
| **Context Preservation** | Context quan trọng có được truyền đầy đủ qua handoff không |

### 19.4. Safety

| Metric | Mô tả |
|--------|--------|
| **Escalation Accuracy** | AI có nhận diện đúng case cần human không |

---

## 20. Future Roadmap

### Phase 1 — MVP

- [ ] Core Agent architecture (Chief + Specialist Agents)
- [ ] Booking workflow (search → book → pay → confirm)
- [ ] Complaint workflow (receive → classify → resolve)
- [ ] Basic RAG for Hiền Hựu service information
- [ ] Human-in-the-Loop approval mechanism
- [ ] API backend
- [ ] Audit Log

### Phase 2 — Customer Service

- [ ] Multi-channel support (Web, Zalo, Facebook)
- [ ] Conversation memory
- [ ] Customer history

### Phase 3 — Business Operations

- [ ] Fleet/Trip Management Agents
- [ ] Revenue Analytics
- [ ] Reporting Dashboard

---

## 21. Giá trị cốt lõi

Dự án hướng tới mô hình:

> **One-person business + AI workforce**

Thay vì chỉ xây dựng chatbot hỏi đáp, hệ thống biến AI thành **lớp vận hành thông minh**:

```text
AI
├── Tiếp nhận yêu cầu
├── Hiểu intent
├── Phối hợp agent
├── Gọi tool
├── Thực hiện workflow
├── Theo dõi state
└── Escalate khi cần
          ↓
   Chủ nhà xe kiểm soát
   quyết định quan trọng
```

---

## 22. Tóm tắt định vị

> **Đây là hệ thống AI Multi-Agent hỗ trợ vận hành cho doanh nghiệp một người Nhà xe Hiền Hựu. AI không chỉ trả lời khách hàng mà có khả năng tự thực hiện nghiệp vụ nhiều bước, gọi công cụ, phối hợp giữa các agent và chuyển các hành động rủi ro cho chủ nhà xe phê duyệt. Toàn bộ hoạt động quan trọng được ghi nhận qua audit log, hướng tới một mô hình "One-person business + AI workforce".**
