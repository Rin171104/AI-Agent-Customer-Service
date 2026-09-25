# Chính Sách Đặt Vé

**DEMO DATA - Chính sách mẫu phục vụ phát triển MVP**

## Quy trình đặt vé

### Bước 1: Tìm chuyến

Tìm chuyến xe phù hợp với ngày và tuyến mong muốn.

### Bước 2: Kiểm tra ghế trống

Xem số ghế còn trống trên chuyến.

> **Lưu ý**: Số ghế trống là dữ liệu realtime → Xem trong hệ thống.

### Bước 3: Chọn số ghế

Chọn số lượng ghế cần đặt.

### Bước 4: Nhập thông tin

Cung cấp các thông tin cần thiết (xem bên dưới).

### Bước 5: Xác nhận booking

Kiểm tra thông tin và xác nhận đặt vé.

### Bước 6: Thanh toán

Thanh toán theo hướng dẫn.

### Bước 7: Nhận mã booking

Sau khi thanh toán thành công, nhận mã booking (VD: BK123456).

## Thông tin cần cung cấp

| Thông tin | Bắt buộc | Ghi chú |
|-----------|-----------|---------|
| Họ tên khách hàng | ✅ | |
| Số điện thoại | ✅ | Để nhận thông tin chuyến xe |
| Điểm đón | ✅ | Theo danh sách điểm đón |
| Điểm trả | ✅ | Theo danh sách điểm trả |
| Ngày khởi hành | ✅ | |
| Số lượng ghế | ✅ | |
| Ngày sinh (nếu có) | ❌ | Tùy chính sách nhà xe |

## Xác nhận đặt vé

- Sau khi đặt thành công, bạn sẽ nhận được **mã booking**
- Vui lòng **giữ mã booking** để check-in và theo dõi

## Thanh toán

- Thanh toán ngay sau khi đặt vé
- Chấp nhận: Chuyển khoản, Ví điện tử
- **Vé chỉ được xác nhận** sau khi thanh toán thành công

## Check-in

- Khách hàng vui lòng có mặt tại **điểm đón trước 15-30 phút**
- Xuất trình **mã booking** hoặc **số điện thoại** khi lên xe

## Lưu ý

- Thông tin chi tiết về booking cụ thể → **Database/BookingTools**
- Thông tin về chính sách đặt vé tổng quát → **RAG**
