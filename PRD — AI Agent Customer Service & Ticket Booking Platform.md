# PRD — AI Agent Customer Service & Ticket Booking Platform

## 1. Tổng quan sản phẩm

### 1.1. Tên sản phẩm

**AI Agent Customer Service & Ticket Booking Platform**

### 1.2. Mô tả

Hệ thống AI Agent hỗ trợ các nhà xe vừa và nhỏ tự động hóa hoạt động **chăm sóc khách hàng, đặt vé, thanh toán và xử lý khiếu nại**.

Thay vì xây dựng một chatbot chỉ trả lời câu hỏi, hệ thống sử dụng kiến trúc **Multi-Agent**, trong đó **Chief Agent** đóng vai trò điều phối trung tâm, tự động phân tích yêu cầu và giao nhiệm vụ cho các Specialist Agent.

Các Specialist Agent chính:

- **Booking Agent:** xử lý nghiệp vụ đặt vé.
- **Complaint Agent:** xử lý khiếu nại.
- **Payment Agent:** xử lý thanh toán.

Các Agent có thể sử dụng những capability chung như:

- RAG / Knowledge Base.
- Database.
- Booking Tools.
- Payment Tools.
- Customer/Trip Management APIs.

Các trường hợp có rủi ro hoặc vượt quá phạm vi xử lý của AI sẽ được chuyển cho nhân viên CSKH thông qua cơ chế **Human-in-the-Loop**.

---

# 2. Problem Statement

Các nhà xe vừa và nhỏ thường có quy mô khoảng 10–50 xe và phải xử lý lượng lớn yêu cầu từ khách hàng mỗi ngày.

Các vấn đề chính:

### 2.1. Tra cứu thủ công

Nhân viên phải kiểm tra thủ công:

- Lịch chạy.
- Tuyến xe.
- Giá vé.
- Ghế trống.
- Thông tin booking.
- Trạng thái thanh toán.

Điều này làm tăng thời gian phản hồi và dễ xảy ra sai sót.

### 2.2. Quy trình đặt vé nhiều bước

Một yêu cầu đặt vé thường cần:

```text
Tìm chuyến
→ Kiểm tra ghế
→ Chọn chuyến
→ Thu thập thông tin
→ Giữ ghế
→ Tạo booking
→ Thanh toán
→ Xác nhận vé
```

Nhân viên phải thực hiện nhiều thao tác lặp lại.

### 2.3. Khiếu nại phân tán

Khách hàng có thể gửi khiếu nại qua nhiều kênh:

- Điện thoại.
- Zalo.
- Facebook.
- Tin nhắn trực tiếp.

Việc quản lý không tập trung có thể dẫn tới bỏ sót hoặc xử lý không nhất quán.

### 2.4. Nhân viên CSKH bị quá tải

Các yêu cầu đơn giản chiếm nhiều thời gian:

- Hỏi giá.
- Hỏi lịch xe.
- Hỏi ghế.
- Đặt vé.
- Kiểm tra booking.
- Kiểm tra thanh toán.

Nhân viên cần tập trung vào các trường hợp phức tạp hơn.

---

# 3. Product Vision

> **Xây dựng một AI Operating System cho hoạt động CSKH của nhà xe, trong đó nhiều AI Agent có thể tự phối hợp để xử lý một nghiệp vụ end-to-end, nhưng vẫn đảm bảo con người kiểm soát các quyết định quan trọng.**

Hệ thống hướng tới workflow:

```text
Customer / CSKH
       ↓
Chief Agent
       ↓
Specialist Agent
       ↓
Tools / RAG / Database
       ↓
Chief Agent
       ↓
Human-in-the-Loop (nếu cần)
       ↓
Business State Updated
```

---

# 4. Product Goals

## 4.1. Mục tiêu chính

1. Tự động hóa các yêu cầu CSKH phổ biến.
2. Tự động hóa quy trình đặt vé end-to-end.
3. Tự động hóa một phần quy trình xử lý khiếu nại.
4. Tự động hóa kiểm tra và xác nhận thanh toán.
5. Cho phép nhiều Agent phối hợp trong cùng một workflow.
6. Giảm số thao tác thủ công của nhân viên CSKH.
7. Đảm bảo AI không tự ý thực hiện các hành động có rủi ro cao.

## 4.2. Mục tiêu về Agentic Behavior

Hệ thống phải thể hiện được:

- Agent tự xác định nghiệp vụ cần xử lý.
- Chief Agent tự động delegate task.
- Specialist Agent thực hiện nghiệp vụ.
- Agent có thể gọi tool.
- Chief Agent theo dõi kết quả.
- Agent có thể handoff sang Agent khác.
- Human được đưa vào workflow khi cần.

---

# 5. Non-Goals

MVP không tập trung vào:

- Xây dựng hệ thống quản lý toàn bộ hoạt động vận tải.
- Tự động điều phối xe ngoài phạm vi booking.
- Tự động quyết định hoàn tiền trong các trường hợp rủi ro cao.
- Thay thế hoàn toàn nhân viên CSKH.
- Xây dựng một marketplace tổng hợp nhiều nhà xe.
- Xây dựng workflow builder cho phép người dùng tự tạo Agent.

---

# 6. Target Users

## 6.1. Khách hàng

Khách hàng sử dụng hệ thống để:

- Hỏi thông tin.
- Tìm chuyến.
- Đặt vé.
- Thanh toán.
- Kiểm tra booking.
- Khiếu nại.

## 6.2. Nhân viên CSKH

Nhân viên sử dụng hệ thống để:

- Theo dõi các yêu cầu của khách hàng.
- Can thiệp vào những trường hợp AI không thể xử lý.
- Phê duyệt các hành động cần Human-in-the-Loop.
- Theo dõi trạng thái booking và complaint.

## 6.3. Chủ nhà xe

Chủ nhà xe có thể theo dõi:

- Booking.
- Doanh thu.
- Thanh toán.
- Tình trạng chuyến.
- Khiếu nại.
- Các vấn đề cần nhân viên xử lý.

---

# 7. Agent Architecture

## 7.1. Chief Agent

### Vai trò

Chief Agent là **Orchestrator** của toàn hệ thống.

Chief Agent không trực tiếp thực hiện các nghiệp vụ như tạo booking hay thanh toán.

### Responsibilities

- Nhận yêu cầu.
- Xác định intent.
- Xác định thông tin còn thiếu.
- Lập kế hoạch xử lý.
- Delegate task cho Specialist Agent.
- Theo dõi trạng thái.
- Nhận kết quả.
- Validate kết quả.
- Quyết định bước tiếp theo.
- Handoff sang Agent khác.
- Kích hoạt Human-in-the-Loop.

### Ví dụ

```text
Customer:
"Tôi muốn đặt 2 vé Sài Gòn đi Đà Lạt tối nay."

Chief Agent:
Intent = BOOKING

→ Delegate Booking Agent
```

---

# 8. Booking Agent

## 8.1. Domain

**Ticket Booking**

## 8.2. Mục tiêu

Xử lý toàn bộ quy trình đặt vé từ việc tìm chuyến đến tạo booking.

## 8.3. Responsibilities

- Tìm kiếm chuyến.
- Kiểm tra ghế.
- Đề xuất chuyến phù hợp.
- Giữ ghế.
- Thu thập thông tin khách hàng.
- Tạo booking draft.
- Kiểm tra trạng thái booking.
- Hủy booking theo policy.

## 8.4. Tools

Ví dụ:

```text
search_trip()
check_available_seats()
hold_seat()
create_booking()
get_booking()
cancel_booking()
```

## 8.5. Workflow

```text
Chief Agent
     ↓
Booking Agent
     ↓
Search Trip
     ↓
Check Seat
     ↓
Customer Select Trip
     ↓
Collect Customer Info
     ↓
Hold Seat
     ↓
Create Booking Draft
     ↓
Chief Agent Validation
     ↓
Customer Confirmation
     ↓
Payment Agent
```

---

# 9. Complaint Agent

## 9.1. Domain

**Customer Complaint Management**

## 9.2. Mục tiêu

Tự động tiếp nhận và hỗ trợ xử lý khiếu nại của khách hàng.

## 9.3. Responsibilities

- Nhận nội dung khiếu nại.
- Phân loại khiếu nại.
- Xác định mức độ nghiêm trọng.
- Tra cứu booking liên quan.
- Thu thập bằng chứng.
- Đề xuất hướng xử lý.
- Tạo complaint ticket.
- Escalate cho nhân viên CSKH khi cần.

## 9.4. Ví dụ loại khiếu nại

```text
- Tài xế bỏ điểm đón
- Trễ chuyến
- Sai thông tin vé
- Vấn đề thanh toán
- Mất đồ
- Thái độ phục vụ
- Yêu cầu hoàn/hủy vé
```

## 9.5. Workflow

```text
Customer
   ↓
Chief Agent
   ↓
Complaint Agent
   ↓
Classify Complaint
   ↓
Retrieve Booking
   ↓
Retrieve Policy / Evidence
   ↓
Generate Resolution
   ↓
 ┌───────────────┐
 │ Low Risk      │ → AI xử lý
 │ High Risk     │ → Human CSKH
 └───────────────┘
```

---

# 10. Payment Agent

## 10.1. Domain

**Payment**

## 10.2. Mục tiêu

Xử lý trạng thái thanh toán và liên kết thanh toán với booking.

## 10.3. Responsibilities

- Tạo payment request.
- Gửi payment information.
- Kiểm tra transaction.
- Xác nhận payment.
- Cập nhật payment status.
- Thông báo kết quả cho Chief Agent.

## 10.4. Tools

```text
create_payment()
check_payment_status()
confirm_payment()
```

## 10.5. Workflow

```text
Booking Draft
      ↓
Customer Confirmation
      ↓
Payment Agent
      ↓
Create Payment
      ↓
Customer Payment
      ↓
Check Payment
      ↓
Payment Success
      ↓
Confirm Booking
```

---

# 11. Shared Capabilities

RAG và Tool **không được coi là Agent**.

## 11.1. RAG / Knowledge Base

Dùng để cung cấp thông tin chính xác từ nguồn dữ liệu được phê duyệt.

Các thông tin có thể gồm:

- Giá vé.
- Chính sách hoàn/hủy.
- Lịch chạy.
- Điểm đón/trả.
- Quy định hành lý.
- Chính sách thanh toán.

Workflow:

```text
Agent
 ↓
Retriever
 ↓
Knowledge Base
 ↓
Relevant Context
 ↓
LLM
```

## 11.2. Database

Lưu trữ:

- Customer.
- Trip.
- Route.
- Seat.
- Booking.
- Payment.
- Complaint.

## 11.3. Tools

Tools thực hiện hành động thực tế.

Ví dụ:

```text
search_trip
check_seat
hold_seat
create_booking
get_booking
create_payment
check_payment
create_complaint
update_complaint
```

---

# 12. Core User Flows

## 12.1. Booking Flow

```text
Customer
  ↓
"I want 2 tickets from HCMC to Da Lat"
  ↓
Chief Agent
  ↓
Booking Agent
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
Payment Agent
  ↓
Payment
  ↓
Confirm Booking
```

---

# 13. Example Booking Conversation

### Customer

> Tôi muốn đặt 2 vé Sài Gòn đi Đà Lạt ngày 20/09.

### Chief Agent

Xác định:

```json
{
  "intent": "booking",
  "origin": "Sài Gòn",
  "destination": "Đà Lạt",
  "date": "2026-09-20",
  "quantity": 2
}
```

→ Delegate Booking Agent.

### Booking Agent

```text
search_trip()
check_available_seats()
```

Kết quả:

```text
Chuyến 22:00
Còn ghế A05, A06
Giá: 250.000đ/vé
```

### Chief Agent

> Chuyến 22:00 ngày 20/09 còn 2 ghế A05 và A06, giá 250.000đ/vé. Bạn có muốn đặt chuyến này không?

### Customer

> Có.

### Booking Agent

```text
hold_seat()
create_booking()
```

### Chief Agent

→ Handoff Payment Agent.

### Payment Agent

```text
create_payment()
check_payment_status()
```

### Payment Success

→ Booking được chuyển sang:

```text
CONFIRMED
```

---

# 14. Complaint Flow

Ví dụ:

> "Tôi đã đặt vé nhưng tài xế không đón tôi ở điểm đã đăng ký."

Workflow:

```text
Customer
   ↓
Chief Agent
   ↓
Complaint Agent
   ↓
Retrieve Booking
   ↓
Retrieve Pickup Information
   ↓
Classify Severity
   ↓
Retrieve Policy
   ↓
Generate Resolution
   ↓
Human Approval nếu cần
   ↓
Update Complaint
```

---

# 15. Human-in-the-Loop

AI không tự quyết định đối với các hành động có rủi ro cao.

Các trường hợp có thể yêu cầu Human Approval:

- Hoàn tiền.
- Bồi thường.
- Khiếu nại nghiêm trọng.
- Hủy booking đặc biệt.
- Thay đổi thông tin quan trọng.
- Yêu cầu ngoài policy.

Ví dụ:

```text
Complaint Agent
      ↓
Refund Request: 300.000đ
      ↓
HITL Gate
      ↓
CSKH Review
      ↓
Approve / Reject / Edit
      ↓
Payment / Booking Tool
```

---

# 16. State Management

Hệ thống cần duy trì shared state trong quá trình Agent phối hợp.

Ví dụ:

```json
{
  "user_id": "...",
  "intent": "booking",

  "origin": "Sài Gòn",
  "destination": "Đà Lạt",
  "travel_date": "2026-09-20",
  "departure_time": "22:00",

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

# 17. Agent Handoff

Handoff phải thể hiện được lý do chuyển giao.

Ví dụ:

```text
Chief Agent
     ↓
"Intent = Booking"
     ↓
Booking Agent
     ↓
"Booking draft created"
     ↓
Chief Agent
     ↓
"Customer confirmed"
     ↓
Payment Agent
```

Một workflow có thể có nhiều handoff:

```text
Chief
  ↓
Booking
  ↓
Chief
  ↓
Payment
  ↓
Chief
```

---

# 18. Live Agent Run

Hệ thống nên hiển thị quá trình Agent thực hiện task.

Ví dụ:

```text
● Chief Agent
  Analyzing request

      ↓

● Booking Agent
  Searching available trips

      ↓

● Booking Agent
  Checking seat availability

      ↓

● Chief Agent
  Waiting for customer confirmation

      ↓

● Payment Agent
  Creating payment request

      ↓

● Payment Agent
  Payment confirmed

      ↓

✓ Chief Agent
  Booking completed
```

Mục đích là giúp người dùng nhìn thấy **Agent đang thực sự phối hợp**, thay vì chỉ nhận một câu trả lời cuối cùng.

---

# 19. Business View

Dashboard dành cho chủ nhà xe.

Các thông tin chính:

```text
Today's Overview

Bookings:              42
Tickets Sold:          87
Available Seats:       53
Revenue:               xxx
Pending Payments:      5
Open Complaints:       3
Need Attention:        2
```

Business View giúp chuyển sản phẩm từ:

> **Chatbot**

thành:

> **AI Operating System cho nhà xe**

---

# 20. Review & Act

Sau khi Agent hoàn thành workflow, Chief Agent tổng hợp:

### Recommendation

```text
Có 3 khiếu nại cần nhân viên xử lý hôm nay.

1. Khiếu nại bỏ điểm đón
   Booking: BK001
   Severity: High

2. Yêu cầu hoàn vé
   Booking: BK002
   Refund: 250.000đ

3. Sai thông tin hành khách
   Booking: BK003
```

Nhân viên có thể:

```text
Approve
Edit
Reject
```

Sau khi approve:

```text
Action
 ↓
External / Mock API
 ↓
Business State Updated
 ↓
Run Completed
```

---

# 21. Functional Requirements

## FR-01 — Intent Detection

System phải xác định được các intent chính:

- Booking.
- Complaint.
- Payment.
- Information / FAQ.
- General / Fallback.

## FR-02 — Agent Routing

Chief Agent phải route request tới Agent phù hợp.

## FR-03 — Multi-Agent Handoff

System phải hỗ trợ Agent handoff trong cùng một workflow.

## FR-04 — Tool Calling

Agent phải có khả năng gọi tool để thực hiện action.

## FR-05 — RAG

Agent phải có khả năng truy xuất knowledge base khi cần thông tin domain.

## FR-06 — Human-in-the-Loop

System phải có cơ chế yêu cầu nhân viên approval.

## FR-07 — State Management

Workflow phải duy trì state xuyên suốt quá trình.

## FR-08 — Audit / Trace

System phải lưu lại:

- Agent nào được gọi.
- Task gì được giao.
- Tool nào được gọi.
- Kết quả.
- Handoff.
- Approval.
- State change.

---

# 22. Non-Functional Requirements

### Reliability

Không được tự ý xác nhận booking nếu chưa có ghế hoặc chưa đáp ứng điều kiện booking.

### Safety

Các hành động có rủi ro phải có Human Approval.

### Traceability

Mọi action của Agent phải có trace.

### Scalability

Có thể bổ sung Agent mới mà không phải thay đổi toàn bộ hệ thống.

### Maintainability

Agent, Tool và Knowledge Base phải được tách biệt.

---

# 23. Suggested Technical Architecture

```text
                    Frontend
                       │
                       ▼
                 FastAPI Backend
                       │
                       ▼
                ┌──────────────┐
                │ Chief Agent  │
                │  LangGraph   │
                └──────┬───────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Booking       Complaint     Payment
       Agent          Agent        Agent
          │            │            │
          └────────────┼────────────┘
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
        Tools         RAG          Database
          │            │             │
          └────────────┼─────────────┘
                       ▼
                 Business State
```

### Technology đề xuất

- **Backend:** Python + FastAPI.
- **Agent orchestration:** LangGraph.
- **LLM:** tùy model triển khai.
- **RAG:** Embedding + Vector Database.
- **Database:** PostgreSQL.
- **Frontend:** React / Next.js.
- **Authentication:** JWT.
- **Observability:** Agent Run / Trace / Audit Log.

---

# 24. MVP Scope

MVP tập trung vào một workflow hoàn chỉnh:

> **Customer → Booking → Payment → Confirmation**

và một workflow thứ hai:

> **Customer → Complaint → Human Approval**

### MVP Agents

```text
1. Chief Agent
2. Booking Agent
3. Complaint Agent
4. Payment Agent
```

### MVP Capabilities

```text
RAG
Database
Booking Tools
Payment Tools
Complaint Tools
Human-in-the-Loop
Agent Trace
```

---

# 25. Golden Demo

Golden Demo đề xuất:

### Step 1 — Customer

> Tôi muốn đặt 2 vé Sài Gòn → Đà Lạt ngày 20/09.

### Step 2 — Chief Agent

Detect Booking → delegate Booking Agent.

### Step 3 — Booking Agent

Search Trip → Check Seat → Create Booking Draft.

### Step 4 — Chief Agent

Hiển thị thông tin và yêu cầu customer confirmation.

### Step 5 — Payment Agent

Create Payment → Check Payment.

### Step 6 — Booking

Payment Success → Confirm Booking.

### Step 7 — Business State

Dashboard cập nhật:

```text
Available Seats: -2
Tickets Sold: +2
Revenue: +500.000đ
Booking: CONFIRMED
Payment: PAID
```

Workflow thể hiện được:

**Chief → Booking → Chief → Payment → Chief**

và có:

- Multi-Agent.
- Autonomous Handoff.
- Tool Calling.
- Shared State.
- Human Confirmation.
- Business State Update.
- Trace / Audit.

---

# 26. Success Metrics

### Booking Success Rate

Tỷ lệ workflow booking hoàn thành thành công.

### Task Completion Rate

Tỷ lệ yêu cầu được xử lý mà không cần nhân viên can thiệp.

### Handoff Accuracy

Tỷ lệ Chief Agent route đúng Specialist Agent.

### Tool Success Rate

Tỷ lệ tool execution thành công.

### Complaint Resolution Rate

Tỷ lệ complaint được xử lý hoặc chuyển đúng tuyến.

### Human Escalation Rate

Tỷ lệ request phải chuyển cho nhân viên.

### Response Time

Thời gian từ khi nhận yêu cầu đến khi hoàn thành workflow.

---

# 27. Product Differentiation

Sản phẩm không chỉ là:

> **AI Chatbot cho nhà xe**

mà là:

> **AI Agent Operating System cho nhà xe**

Điểm khác biệt nằm ở khả năng:

```text
Understand
    ↓
Plan
    ↓
Delegate
    ↓
Execute
    ↓
Validate
    ↓
Ask Human
    ↓
Act
    ↓
Update Business State
```

Thay vì chỉ:

```text
User
 ↓
LLM
 ↓
Answer
```

hệ thống có thể thực hiện **end-to-end business workflow** thông qua nhiều Agent phối hợp.

---

# 28. Future Roadmap

Sau MVP có thể mở rộng:

### Phase 2 — Customer Service

- Multi-channel: Zalo / Facebook / Web.
- Conversation memory.
- Customer history.
- Automated FAQ.

### Phase 3 — Business Operations

- Revenue Agent.
- Reporting Agent.
- Fleet/Trip Management Agent.
- Business Analytics Agent.

### Phase 4 — AI Operating System

Mở rộng Business View:

```text
Ask:
"Hôm nay nhà xe có vấn đề gì cần xử lý?"
```

Chief Agent tự động:

```text
Analyze Business State
       ↓
Delegate Agents
       ↓
Collect Results
       ↓
Prioritize Issues
       ↓
Generate Recommendation
       ↓
Human Approval
       ↓
Execute Action
```

Mục tiêu cuối cùng là xây dựng một **AI-native operating layer** cho hoạt động vận hành và CSKH của nhà xe.