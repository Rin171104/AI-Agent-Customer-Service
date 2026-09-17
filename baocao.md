# BÁO CÁO MÔ TẢ DỰ ÁN

## AI Multi-Agent Operations Assistant cho Nhà xe Hiền Hựu

---

## 1. Tên đề tài & Định vị

### Tên đề tài

**Xây dựng hệ thống AI Multi-Agent hỗ trợ CSKH và vận hành cho doanh nghiệp một người – Nhà xe Hiền Hựu**

### Định vị

Dự án xây dựng một hệ thống **AI Operations Assistant** giúp chủ nhà xe tự động hóa phần lớn hoạt động CSKH và vận hành hằng ngày.

AI đóng vai trò như một **đội ngũ vận hành ảo**: tiếp nhận yêu cầu, tự thực hiện nhiều bước, gọi công cụ, phối hợp giữa các agent và chỉ chuyển cho chủ nhà xe những quyết định có rủi ro hoặc cần quyền con người.

Hệ thống tập trung vào 4 tiêu chí chính:

1. **Bot làm việc thật:** nhận việc, tự chạy nhiều bước và gọi tool.
2. **Phối hợp:** nhiều agent phối hợp và handoff kèm context.
3. **Quản trị mặc định:** hành động rủi ro cần human approval và có audit log.
4. **Đích đến:** có Hero Flow hoàn chỉnh từ Chat → Handoff → Làm việc → Duyệt → Audit.

Phạm vi MVP:

- Tư vấn và tra cứu thông tin.
- Đặt vé và thanh toán.
- Tra cứu booking.
- Tiếp nhận và xử lý khiếu nại.
- Tạo và theo dõi yêu cầu hoàn tiền.

---

## 2. Pain Point & Evidence

### Pain Point

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

### Giải pháp

AI xử lý các công việc có thể chuẩn hóa và tự động hóa:

```text
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

### Evidence

Dữ liệu công khai về nhà xe có thể khác nhau giữa các nguồn về lịch trình, giá hoặc dịch vụ. Vì vậy, hệ thống phân biệt:

- **Kiến thức tương đối ổn định → RAG**
- **Dữ liệu giao dịch/realtime → Tools + Database**

RAG không được sử dụng như nguồn dữ liệu realtime về số ghế, booking hoặc trạng thái thanh toán.

---

## 3. User & Context

Hệ thống có 2 nhóm người dùng chính.

### 3.1. Khách hàng

Khách hàng tương tác với AI để:

- Hỏi thông tin nhà xe.
- Hỏi lịch trình.
- Kiểm tra ghế.
- Đặt vé.
- Thanh toán.
- Tra cứu booking.
- Gửi khiếu nại.
- Yêu cầu hoàn tiền.

### 3.2. Chủ nhà xe

Chủ nhà xe sử dụng hệ thống để:

- Theo dõi booking.
- Theo dõi khiếu nại.
- Xem các yêu cầu cần xử lý.
- Duyệt các nghiệp vụ có rủi ro.
- Thực hiện hoàn tiền.
- Theo dõi audit log và lịch sử hoạt động của AI.

### Context

Mô hình vận hành hướng tới:

```text
              AI OPERATIONS SYSTEM
             /                    \
            ↓                      ↓
      KHÁCH HÀNG              CHỦ NHÀ XE
            ↕                      ↕
          Chat                Approval
```

AI trở thành lớp vận hành trung gian, giúp chủ nhà xe giảm tải các công việc thường ngày nhưng vẫn giữ quyền kiểm soát các quyết định quan trọng.

---

## 4. Multi-Agent

Kiến trúc sử dụng **Chief Agent + Specialist Agents**.

```text
                    Chief Agent
                   /            \
                  ↓              ↓
      Booking & Payment     Complaint Agent
             Agent                Agent
                  \              /
                   ↓            ↓
              Tools + RAG + DB
```

### 4.1. Chief Agent

Chief Agent là **orchestrator** của hệ thống.

Nhiệm vụ:

- Hiểu yêu cầu của khách.
- Xác định intent.
- Lập kế hoạch xử lý.
- Handoff cho agent phù hợp.
- Truyền context giữa các bước.
- Theo dõi kết quả.
- Validate kết quả.
- Quyết định trả lời tự động hoặc chuyển Human-in-the-loop.

Flow:

```text
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

### 4.2. Booking & Payment Agent

Phụ trách toàn bộ workflow giao dịch:

- Tìm chuyến.
- Xem chi tiết chuyến.
- Kiểm tra ghế.
- Giữ ghế.
- Tạo booking.
- Thu thập thông tin khách.
- Xác nhận booking.
- Theo dõi trạng thái thanh toán.

Ví dụ tools:

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

### 4.3. Complaint Agent

Phụ trách:

- Tiếp nhận khiếu nại.
- Phân loại vấn đề.
- Tra cứu booking.
- Tra cứu chính sách.
- Phân tích mức độ nghiêm trọng.
- Đề xuất hướng xử lý.
- Tạo complaint/refund request.
- Escalate cho chủ nhà xe khi cần.

Một số loại khiếu nại:

```text
WRONG_SEAT
LATE_DEPARTURE
DRIVER_BEHAVIOR
LOST_ITEM
PAYMENT
BOOKING_ERROR
REFUND
OTHER
```

---

## 5. Bot làm việc thật

Tiêu chí quan trọng của hệ thống là AI phải **thực sự thực hiện nghiệp vụ**, không chỉ sinh câu trả lời.

Ví dụ khách yêu cầu:

> “Đặt 2 vé Hà Nội đi Tà Xùa tối nay.”

AI thực hiện nhiều bước:

```text
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

Điểm thể hiện:

- Multi-step reasoning.
- Tool calling.
- State management.
- Business data access.
- End-to-end task execution.

---

## 6. Phối hợp & Handoff

Các agent không hoạt động độc lập mà phối hợp thông qua **handoff kèm context**.

Ví dụ:

```text
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

Context có thể bao gồm:

```text
user_id
intent
origin
destination
travel_date
trip_id
customer_info
booking_id
payment_status
complaint_id
requires_human
```

Với khiếu nại:

```text
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

## 7. RAG, Tools và Database

Hệ thống phân tách rõ giữa **knowledge** và **business data**.

### RAG

Sử dụng cho:

- Thông tin nhà xe.
- Thông tin tuyến.
- Dịch vụ.
- FAQ.
- Chính sách đặt/hủy/hoàn vé.
- Điểm đón/trả.

### Tools + Database

Sử dụng cho:

- Chuyến hiện tại.
- Số ghế còn lại.
- Booking.
- Customer.
- Payment.
- Complaint.
- Refund request.

Nguyên tắc:

> **RAG trả lời “nhà xe quy định/cung cấp gì”.**

> **Tool + Database trả lời “hiện tại hệ thống đang có gì”.**

Ví dụ:

```text
“Chính sách hoàn vé là gì?”
        → RAG

“Chuyến tối nay còn bao nhiêu ghế?”
        → Tool → Database

“Booking của tôi đang ở trạng thái nào?”
        → Tool → Database
```

---

## 8. Quản trị mặc định & Human-in-the-loop

Hệ thống áp dụng nguyên tắc:

> **AI có thể tự động xử lý công việc, nhưng hành động có rủi ro phải có human control.**

### AI có thể tự động xử lý

- FAQ.
- Tra cứu thông tin.
- Kiểm tra chuyến.
- Kiểm tra ghế.
- Tạo booking.
- Tra cứu payment status.
- Tiếp nhận và phân loại khiếu nại.

### Cần chủ nhà xe kiểm soát

- Hoàn tiền.
- Tranh chấp.
- Khiếu nại nghiêm trọng.
- Yêu cầu ngoài chính sách.
- Các hành động có tác động tài chính.
- Trường hợp AI không đủ thông tin/confidence.

### Refund Flow

```text
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

AI **không trực tiếp chuyển tiền**. AI tạo, theo dõi và cập nhật yêu cầu; chủ nhà xe thực hiện giao dịch thực tế.

---

## 9. Audit Log

Mọi hành động quan trọng của Agent cần có trace/audit log.

Thông tin cần lưu:

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

Ví dụ:

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

Audit log giúp:

- Theo dõi AI đã làm gì.
- Debug workflow.
- Kiểm tra các quyết định.
- Truy vết nghiệp vụ.
- Tăng khả năng kiểm soát hệ thống.

---

## 10. Hero Flow

Hero Flow cần thể hiện đầy đủ tiêu chí:

> **Chat → Handoff → Làm việc → Duyệt → Audit**

### Hero Flow: Xử lý yêu cầu hoàn tiền

```text
CUSTOMER
“Tôi muốn hoàn tiền vé này”
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

Hero Flow này đồng thời thể hiện:

| Tiêu chí | Cách đáp ứng |
|---|---|
| Bot làm việc thật | Agent gọi Tool + RAG + DB và thực hiện nhiều bước |
| Phối hợp | Chief Agent → Complaint Agent → Human |
| Handoff | Truyền booking/context giữa các bước |
| Quản trị | Human approval trước hành động rủi ro |
| Audit | Ghi lại toàn bộ action và kết quả |
| Đích đến | Chat → Handoff → Work → Approve → Audit |

---

## 11. Evaluation & Metric

### RAG

- **Recall@5:** Context liên quan có xuất hiện trong top-5 hay không.
- **Context Accuracy:** Context được retrieve có chính xác/phù hợp không.
- **Faithfulness:** Câu trả lời có bám vào context không.

### Agent

- **Tool Calling Accuracy:** Agent có chọn và gọi đúng tool không.
- **Task Completion:** Workflow có hoàn thành đúng mục tiêu không.

### Multi-Agent

- **Handoff Accuracy:** Agent có chuyển đúng workflow/agent không.
- **Context Preservation:** Context quan trọng có được truyền đầy đủ qua handoff không.

### Safety

- **Escalation Accuracy:** AI có nhận diện đúng case cần human không.

---

## 12. Kiến trúc tổng thể

```text
                         ┌───────────────┐
                         │   CUSTOMER    │
                         └───────┬───────┘
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
          │      Agent       │       │                 │
          └────────┬─────────┘       └────────┬────────┘
                   │                          │
                   └───────────┬──────────────┘
                               ▼
                     ┌────────────────────┐
                     │   RAG / Tools / DB │
                     └──────────┬─────────┘
                                │
                         Risk / Guardrail
                                │
                       ┌────────┴────────┐
                       ▼                 ▼
                 Auto Response     ┌──────────────┐
                       │           │ Chủ nhà xe  │
                       │           │   Approval  │
                       │           └──────┬───────┘
                       │                  │
                       └─────────┬────────┘
                                 ▼
                            Audit Log
                                 │
                                 ▼
                              CUSTOMER
```

---

## 13. Công nghệ dự kiến

| Thành phần | Công nghệ |
|---|---|
| Frontend | Node.js |
| Backend | Python + FastAPI |
| Agent Framework | LangGraph |
| LLM Orchestration | LangChain |
| RAG | Embedding + Vector Database |
| Database | PostgreSQL |
| API | REST API |
| Business Data | Tools + PostgreSQL |
| Human-in-the-loop | Owner Dashboard |
| Evaluation | Custom Evaluation Pipeline |

---

## 14. Giá trị cốt lõi

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

### Tóm tắt định vị

> **Đây là hệ thống AI Multi-Agent hỗ trợ vận hành cho doanh nghiệp một người. AI không chỉ trả lời khách hàng mà có khả năng tự thực hiện nghiệp vụ nhiều bước, gọi công cụ, phối hợp giữa các agent và chuyển các hành động rủi ro cho chủ nhà xe phê duyệt. Toàn bộ hoạt động quan trọng được ghi nhận qua audit log, hướng tới một mô hình “One-person business + AI workforce”.**
