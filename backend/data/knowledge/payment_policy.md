# Chính Sách Thanh Toán

**DEMO PAYMENT - Dữ liệu mẫu phục vụ phát triển MVP**

> **Lưu ý**: Đây là mô tả chính sách thanh toán DEMO. Không thực hiện giao dịch tiền thật dựa trên thông tin trong tài liệu này.

## Phương thức thanh toán (DEMO)

### 1. Chuyển khoản ngân hàng

> Thông tin tài khoản sẽ được cập nhật khi có dữ liệu thực tế.

- **Ngân hàng**: [Sẽ được cập nhật]
- **Số tài khoản**: [Sẽ được cập nhật]
- **Tên tài khoản**: [Sẽ được cập nhật]
- **Nội dung chuyển khoản**: [Mã booking] + [Số điện thoại]

### 2. Ví điện tử

Các ví điện tử được hỗ trợ sẽ được cập nhật.

### 3. Thanh toán tại quầy

Tại văn phòng nhà xe hoặc các điểm giao dịch.

## Quy trình thanh toán (DEMO)

### Qua chuyển khoản

1. Đặt vé và nhận mã booking
2. Chuyển khoản đúng số tiền
3. Nội dung: Mã booking + Số điện thoại
4. Đợi xác nhận
5. Nhận thông báo xác nhận thanh toán

### Thanh toán bằng ví điện tử

1. Chọn phương thức ví điện tử
2. Quét mã QR hoặc nhập thông tin
3. Xác nhận thanh toán
4. Nhận xác nhận tức thì

## Xác nhận thanh toán

- **Thanh toán thành công**: Bạn sẽ nhận được thông báo
- **Chưa xác nhận**: Vui lòng kiểm tra lại hoặc liên hệ hỗ trợ

## Phân biệt nguồn dữ liệu

### RAG xử lý (Knowledge)

> "Nhà xe hỗ trợ những phương thức thanh toán nào?"

→ Tài liệu này (RAG)

> "Chính sách thanh toán thế nào?"

→ Tài liệu này (RAG)

### Tool/Database xử lý (Realtime)

> "Booking BK001 đã thanh toán chưa?"

→ **PaymentTools / Database**

> "Tôi đã thanh toán nhưng chưa nhận xác nhận?"

→ **PaymentTools / Database**

> "Số dư tài khoản của tôi?"

→ **PaymentTools / Database**

## Lưu ý

- **Vé chỉ được xác nhận** khi nhà xe nhận đủ tiền
- Nếu chuyển thiếu, vui lòng chuyển thêm phần còn thiếu
- Giữ biên lai/chứng từ chuyển khoản để đối chiếu

## Hóa đơn

[Hướng dẫn xuất hóa đơn sẽ được cập nhật]

## Demo vs Production

| Môi trường | Trạng thái |
|-------------|------------|
| Demo/MVP | Chỉ mô phỏng, không có giao dịch thật |
| Production | Sử dụng thông tin tài khoản thực tế |
