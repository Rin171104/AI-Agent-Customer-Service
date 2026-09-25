# Câu Hỏi Thường Gặp (FAQ)

**DEMO DATA - FAQ mẫu**

> **Lưu ý**: Các câu trả lời chi tiết về policy nằm ở các file riêng:
> - booking_policy.md
> - cancellation_policy.md
> - refund_policy.md
> - payment_policy.md

## Về tuyến xe

**H: Nhà xe chạy tuyến nào?**
T: Nhà xe Hiền Hựu hoạt động trên tuyến Hà Nội - Bắc Yên - Tà Xùa.

**H: Tà Xùa thuộc tỉnh nào?**
T: Tà Xùa thuộc huyện Bắc Yên, tỉnh Sơn La.

**H: Từ Hà Nội đi Tà Xùa mất bao lâu?**
T: Thời gian di chuyển phụ thuộc vào điều kiện đường sá và thời tiết. Vui lòng kiểm tra lịch trình cụ thể trong hệ thống.

## Về đặt vé

**H: Làm sao để đặt vé?**
T: Bạn có thể đặt vé qua AI Chat trên website/app hoặc liên hệ trực tiếp.

**H: Tôi cần cung cấp thông tin gì khi đặt vé?**
T: Họ tên, số điện thoại, điểm đón, điểm trả, ngày khởi hành, số ghế.

**H: Đặt vé trước bao lâu?**
T: Có thể đặt trước [Số ngày sẽ được cập nhật].

**H: Có cần đăng ký tài khoản không?**
T: Không bắt buộc. Bạn có thể đặt vé với tư cách khách.

## Về thanh toán

**H: Tôi có thể thanh toán bằng cách nào?**
T: Các phương thức thanh toán được hỗ trợ: Chuyển khoản, Ví điện tử, Thanh toán tại quầy. Chi tiết trong payment_policy.md.

**H: Thanh toán xong trong bao lâu thì được xác nhận?**
T: Thường trong vài phút đến 30 phút.

**H: Tôi chuyển khoản nhầm số tiền thì sao?**
T: Liên hệ hỗ trợ để được điều chỉnh.

## Về hủy vé

**H: Tôi có thể hủy vé không?**
T: Có, bạn có thể hủy vé theo chính sách hủy vé. Chi tiết trong cancellation_policy.md.

**H: Hủy vé có mất phí không?**
T: Có, phí hủy phụ thuộc vào thời điểm hủy. Xem bảng phí trong cancellation_policy.md.

**H: Tiền hoàn sẽ được chuyển trong bao lâu?**
T: Sau khi hủy và được duyệt, tiền hoàn sẽ được xử lý trong [Số ngày sẽ được cập nhật].

## Về hoàn tiền

**H: Khi nào tôi được hoàn tiền?**
T: Khi hủy vé đúng hạn (theo bảng phí), hoặc khi yêu cầu hoàn tiền được chấp thuận.

**H: Ai duyệt hoàn tiền?**
T: Owner (người quản lý nhà xe) sẽ xem xét và duyệt hoàn tiền. AI chỉ tiếp nhận yêu cầu, không tự quyết định hoàn tiền.

**H: Hoàn tiền cho ai?**
T: Chỉ hoàn tiền cho tài khoản mang tên người đặt vé.

**H: Tôi cần cung cấp thông tin gì để nhận hoàn tiền?**
T: Số tài khoản, tên ngân hàng, tên chủ tài khoản (phải trùng với tên đặt vé).

## Về khiếu nại

**H: Tôi muốn khiếu nại thì làm sao?**
T: Gửi khiếu nại qua AI Chat hoặc liên hệ trực tiếp. Chúng tôi sẽ phản hồi trong thời gian sớm nhất.

**H: Thời gian xử lý khiếu nại là bao lâu?**
T: Thường [Số ngày sẽ được cập nhật] ngày làm việc.

## Về điểm đón/trả

**H: Xe có đón tận nơi không?**
T: Nhà xe hỗ trợ đón tại các điểm trên tuyến. Vui lòng xem chi tiết trong pickup_dropoff.md.

**H: Điểm đón trả trên tuyến Hà Nội - Tà Xùa?**
T: Các điểm đón/trả được hỗ trợ: Hà Nội, Bắc Yên, Tà Xùa và một số điểm trung gian.

## Khác

**H: Tôi quên mã booking thì sao?**
T: Cung cấp số điện thoại đã đặt, chúng tôi sẽ tra cứu.

**H: Tôi muốn đổi sang chuyến khác thì sao?**
T: Liên hệ để được hỗ trợ đổi chuyến (tùy tình trạng ghế trống).

## Phân biệt nguồn thông tin

| Câu hỏi | Nguồn |
|---------|--------|
| Nhà xe có tuyến nào? | RAG |
| Chuyến ngày mai còn ghế không? | Database/Tools |
| Chính sách hoàn tiền? | RAG |
| Refund BK001 đang ở đâu? | Database/Tools |
| Booking của tôi đã thanh toán chưa? | Database/Tools |
| Tôi có được hoàn tiền không? | RAG + Database |
