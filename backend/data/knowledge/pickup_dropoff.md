# Điểm Đón - Trả Khách

**DEMO DATA - Thông tin mẫu**

## Khu vực phục vụ

Nhà xe Hiền Hựu hoạt động trên tuyến miền núi phía Bắc:

```
Hà Nội
   ↕
Bắc Yên (Sơn La)
   ↕
Tà Xùa
```

## Điểm đón/trả (DEMO)

### Hà Nội

> Thông tin điểm đón/trả tại Hà Nội sẽ được cập nhật.

- **Bến xe**: [Sẽ được cập nhật]
- **Điểm trung chuyển**: [Sẽ được cập nhật]

### Bắc Yên

> Thông tin điểm đón/trả tại Bắc Yên sẽ được cập nhật.

- **Trung tâm huyện**: [Sẽ được cập nhật]
- **Các điểm khác**: [Sẽ được cập nhật]

### Tà Xùa

> Thông tin điểm đón/trả tại Tà Xùa sẽ được cập nhật.

- **Trung tâm thị trấn**: [Sẽ được cập nhật]
- **Các điểm du lịch**: [Sẽ được cập nhật]

## Lưu ý chung

### Trước khi khởi hành

- Có mặt tại **điểm đón trước 15-30 phút**
- Liên hệ tài xế qua số điện thoại trên booking
- Chuẩn bị sẵn **mã booking** để check-in

### Thông tin liên hệ tài xế

- Số điện thoại tài xế sẽ được gửi qua SMS trước giờ khởi hành
- Vui lòng liên hệ nếu không nhận được thông tin

### Thay đổi điểm đón/trả

- Thông báo trước để được sắp xếp
- Có thể phát sinh phí nếu thay đổi điểm đón ngoài lộ trình

### Trẻ em và hành lý

| Loại | Quy định |
|------|----------|
| Trẻ em dưới 6 tuổi | Miễn phí (ngồi cùng cha mẹ, không chiếm ghế) |
| Trẻ em trên 6 tuổi | Mua vé như người lớn |
| Hành lý | [Sẽ được cập nhật] |

## Phân biệt nguồn dữ liệu

### RAG xử lý (Knowledge)

> "Nhà xe có hỗ trợ đón tại khu vực nào?"

→ Tài liệu này (RAG)

> "Tà Xùa có điểm đón không?"

→ Tài liệu này (RAG)

> "Điểm đón trả trên tuyến Hà Nội - Tà Xùa?"

→ Tài liệu này (RAG)

### Tool/Database xử lý (Realtime)

> "Booking BK001 đón ở đâu?"

→ **BookingTools / Database**

> "Tôi muốn đổi điểm đón cho booking BK001?"

→ **BookingTools / Database**

> "Điểm đón của chuyến ngày mai?"

→ **TripTools / Database**

## Lưu ý

- Điểm đón/trả cụ thể cho **booking của bạn** → Xem trong hệ thống
- Điểm đón/trả **được hỗ trợ trên tuyến** → Tài liệu này (RAG)
- Thông tin điểm đón có thể thay đổi theo điều kiện thực tế
