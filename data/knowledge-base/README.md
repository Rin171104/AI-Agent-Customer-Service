# Knowledge Base

> ⚠️ **Placeholder** — Nội dung cần được cập nhật từ nguồn thực tế của Nhà xe Hiền Hựu.

## Ghi chú

Knowledge Base cần chứa thông tin được phê duyệt về dịch vụ của Nhà xe Hiền Hựu.

**KHÔNG tự tạo thông tin giả về:**
- Giá vé
- Lịch trình
- Chính sách hoàn/hủy
- Điểm đón/trả
- Loại xe

Các nguồn tham khảo để thu thập thông tin thực:
- Website chính thức của Nhà xe Hiền Hựu
- Vexere.com
- SaoDiều.vn
- Facebook page của Nhà xe Hiền Hựu

## Cấu trúc đề xuất

```
knowledge-base/
├── README.md           # File này
├── service-info.md    # Thông tin dịch vụ chung
├── vehicles.md        # Thông tin loại xe
├── routes.md          # Thông tin tuyến
├── policies.md        # Chính sách (cần xác minh)
├── faq.md            # Câu hỏi thường gặp
└── pickup-points.md  # Điểm đón/trả
```

## Nguyên tắc

1. **RAG trả lời:** "Nhà xe quy định/cung cấp gì"
2. **Tool + Database trả lời:** "Hiện tại hệ thống đang có gì"

Ví dụ:
- "Chính sách hoàn vé là gì?" → RAG (knowledge base)
- "Chuyến tối nay còn bao nhiêu ghế?" → Tool → Database
- "Booking của tôi ở trạng thái nào?" → Tool → Database
