# Chính Sách Hoàn Tiền

**DEMO DATA - Chính sách mẫu**

> **QUAN TRỌNG**: Đọc kỹ phần "Quy trình hoàn tiền" bên dưới.

## Điều kiện được hoàn tiền

### Hoàn tiền khi hủy vé

- **Hủy vé đúng hạn**: Tiền được hoàn theo bảng phí hủy
- **Xe không khởi hành**: Hoàn 100% tiền vé

### Yêu cầu hoàn tiền thủ công

Các trường hợp cần yêu cầu hoàn tiền:

- Đã hủy vé nhưng chưa nhận được tiền hoàn
- Hoàn tiền cho các trường hợp đặc biệt
- Khiếu nại được chấp thuận

## Quy trình hoàn tiền

```
Customer yêu cầu hoàn tiền
   ↓
AI Agent (Complaint Agent)
   ↓
Kiểm tra booking hợp lệ
   ↓
Kiểm tra điều kiện theo policy
   ↓
Tạo refund request
   ↓
Trạng thái: WAITING_OWNER_APPROVAL
   ↓
[Human-in-the-Loop]
   ↓
Owner xem xét và DUYỆT hoặc TỪ CHỐI
   ↓
Nếu duyệt → Owner hoàn tiền THỦ CÔNG
```

## Nguyên tắc quan trọng

### ✅ AI có thể làm

- Tiếp nhận yêu cầu hoàn tiền từ khách
- Kiểm tra booking có tồn tại và thuộc về khách
- Kiểm tra điều kiện hoàn tiền theo policy
- Tạo refund request với trạng thái `WAITING_OWNER_APPROVAL`
- Thu thập thông tin tài khoản ngân hàng của khách

### ❌ AI KHÔNG được làm

- Tự quyết định hoàn tiền
- Tự chuyển tiền cho khách
- Tự phê duyệt refund
- Bypass quy trình Owner approval

### 👤 Chỉ Owner được làm

- Phê duyệt (approve) hoặc từ chối (reject) refund request
- Thực hiện hoàn tiền thủ công (chuyển khoản)
- Đánh dấu refund đã hoàn tiền

## Thông tin cần cung cấp

Để nhận hoàn tiền, quý khách cần cung cấp:

| Thông tin | Bắt buộc | Ghi chú |
|-----------|-----------|---------|
| Mã booking | ✅ | Mã vé gốc cần hoàn tiền |
| Số tài khoản | ✅ | Số tài khoản ngân hàng |
| Tên ngân hàng | ✅ | VD: Vietcombank, BIDV... |
| Tên chủ tài khoản | ✅ | Phải trùng với tên đăng ký booking |

> **Lưu ý**: Thông tin tài khoản chỉ để Owner xử lý hoàn tiền thủ công, không phải để AI tự động chuyển tiền.

## Thời gian xử lý

| Loại hoàn tiền | Thời gian |
|----------------|-----------|
| Hủy vé tự động | [Sẽ được cập nhật] |
| Yêu cầu hoàn tiền | [Sẽ được cập nhật] |

## Lưu ý quan trọng

- **Hoàn tiền chuyển khoản**: Chỉ chuyển đến tài khoản mang tên chủ booking
- **Không hoàn tiền mặt**
- **Phí chuyển khoản**: [Theo chính sách nhà xe]

## Trạng thái refund

Xem chi tiết trạng thái refund: **RefundTools / Database**

Ví dụ:
- "Refund BK001 đang ở trạng thái nào?" → **RefundTools**
- "Tôi có được hoàn tiền không?" → **RAG** (policy)

## Đồng bộ với cancellation_policy

Xem: **cancellation_policy.md** để biết bảng phí hủy vé tương ứng.
