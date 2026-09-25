# Chính Sách Hủy Vé

**DEMO DATA - Chính sách mẫu**

> **Đồng bộ với refund_policy.md** - Vui lòng đọc cả hai file.

## Điều kiện hủy vé

### Hủy trước giờ khởi hành

| Thời điểm hủy | Phí hủy | Số tiền được hoàn |
|----------------|----------|-------------------|
| Trước 24 giờ | 0% | 100% |
| 12-24 giờ | 10% | 90% |
| 6-12 giờ | 20% | 80% |
| 3-6 giờ | 30% | 70% |
| Dưới 3 giờ | 50% | 50% |

> **Lưu ý**: Bảng trên là DEMO DATA. Giá trị thực tế sẽ được cập nhật theo chính sách của nhà xe.

### Không có mặt (No-show)

- Không hoàn tiền
- Vé không có giá trị

### Hủy do nhà xe (xe không chạy)

- Hoàn tiền 100%
- Hỗ trợ chuyển sang chuyến khác miễn phí (nếu có)

## Cách hủy vé

### Qua AI Chat

1. Cung cấp mã booking
2. Xác nhận hủy
3. Tiền hoàn sẽ được xử lý theo chính sách

### Qua hotline

[Liên hệ hotline để được hỗ trợ hủy vé]

## Quy trình hoàn tiền sau hủy

```
Hủy vé
   ↓
Tính phí theo bảng trên
   ↓
Tạo refund request (nếu có số tiền hoàn)
   ↓
WAITING_OWNER_APPROVAL
   ↓
Owner xem xét và duyệt
   ↓
Owner hoàn tiền thủ công
```

> **Quan trọng**: AI chỉ tạo yêu cầu hoàn tiền. Owner là người phê duyệt và thực hiện hoàn tiền.

## Lưu ý

- Việc hủy vé phải được thực hiện **trước giờ khởi hành**
- Không hủy vé sau khi xe đã khởi hành
- Thời gian hoàn tiền: [Sẽ được cập nhật]

## Chi tiết về hoàn tiền

Xem: **refund_policy.md**
