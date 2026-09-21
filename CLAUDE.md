# AI-Agent-Customer-Service

Quy ước chung của dự án (áp dụng cho mọi AI tool): @AGENTS.md

Phần dưới chỉ dành riêng cho Claude Code.

## Nguyên tắc hành vi

Giảm thiểu các lỗi LLM phổ biến khi viết code.

**Ưu tiên:** Cẩn thận hơn tốc độ. Việc đơn giản, ưu tiên cho công việc nhỏ.

### 1. Suy nghĩ trước khi code

**Không giả định. Không che giấu sự bối rối. Nêu rõ các tradeoffs.**

Trước khi implement:
- Nêu rõ các giả định của bạn. Nếu không chắc, hỏi.
- Nếu có nhiều cách diễn giải, trình bày tất cả - đừng chọn âm thầm.
- Nếu có cách đơn giản hơn, nói ra. Phản đối khi cần thiết.
- Nếu có gì không rõ, dừng lại. Đặt tên điều gây confuse. Hỏi.

### 2. Đơn giản trước

**Code tối thiểu giải quyết vấn đề. Không có thứ gì suy đoán.**

- Không có tính năng ngoài yêu cầu.
- Không có abstraction cho code dùng một lần.
- Không có "linh hoạt" hay "cấu hình" không được yêu cầu.
- Không có xử lý lỗi cho kịch bản không thể.
- Nếu viết 200 dòng mà có thể 50 dòng, viết lại.

Tự hỏi: "Senior engineer sẽ nói đây là overcomplicated?" Nếu có, đơn giản hóa.

### 3. Thay đổi chính xác

**Chỉ sửa những gì cần. Dọn dẹp chỉ thứ mình làm.**

Khi edit code có sẵn:
- Không "cải thiện" code, comment, formatting xung quanh.
- Không refactor thứ không hỏng.
- Match style có sẵn, kể cả khi bạn làm khác.
- Nếu thấy dead code không liên quan, đề cập - đừng xóa.

Khi thay đổi tạo orphan:
- Xóa imports/variables/functions mà THAY ĐỔI CỦA BẠN làm thừa.
- Không xóa dead code có sẵn trừ khi được yêu cầu.

Test: Mỗi dòng thay đổi phải trace trực tiếp đến yêu cầu của user.

### 4. Thực thi theo mục tiêu

**Định nghĩa criteria thành công. Lặp cho đến khi verified.**

Chuyển task thành mục tiêu có thể verify:
- "Thêm validation" → "Viết tests cho invalid inputs, rồi làm cho pass"
- "Fix bug" → "Viết test reproduce bug, rồi làm cho pass"
- "Refactor X" → "Đảm bảo tests pass trước và sau"

Với multi-step tasks, nêu brief plan:
```
1. [Bước] → verify: [kiểm tra]
2. [Bước] → verify: [kiểm tra]
3. [Bước] → verify: [kiểm tra]
```

Criteria thành công mạnh cho phép lặp độc lập. Criteria yếu ("làm cho work") cần clarification liên tục.

---

**Guidelines đang hoạt động nếu:** ít thay đổi không cần thiết trong diffs, ít viết lại do overcomplication, và câu hỏi làm rõ đến trước khi implement thay vì sau mistake.

## Skill có sẵn
Chưa dùng, khi nào dùng tôi sẽ sửa.

Skill nằm ở `.claude/skills/<tên>/SKILL.md`, được commit lên git nên cả team dùng chung.
Chú ý, chỉ thay đổi file trong thư mục này. Các thay đổi ở bên ngoài đều không được phép.

## File không được sửa

`.claude/settings.json` chứa hook logging của BTC (`UserPromptSubmit`, `PostToolUse`, `Stop`). Mọi tool call trong phiên đều được ghi vào `.ai-log/session.jsonl` rồi gửi lên grading server khi `git push`. Không sửa file này.

Cấu hình cá nhân (permission, env riêng) đặt ở `.claude/settings.local.json` — và nhớ thêm dòng đó vào `.gitignore` để không đè lên file của BTC.

## Lệnh trên Windows

Máy dev dùng PowerShell. Một số target trong `Makefile` viết theo POSIX nên không chạy trực tiếp được — dùng lệnh gốc thay thế:

```powershell
# Chạy backend
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Chạy seed data
python seed_data.py

# Chạy frontend
cd ../frontend
npm run dev

# Chạy test
pytest tests/ -v

# Kiểm tra code
ruff check src/ tests/
```

## Deployment

Luôn khởi động lại service được thêm tính năng mới để cập nhật trên link production thông qua cloudflare.

## Cấu trúc dự án

```
AI-Agent-Customer-Service/
├── backend/           # FastAPI backend
│   ├── main.py       # Entry point
│   ├── seed_data.py  # Tạo dữ liệu mẫu
│   └── src/          # Source code
├── frontend/          # React + Vite frontend
│   └── src/          # Source code
└── docker-compose.yml # PostgreSQL
```

## Tài khoản demo

| Vai trò | Email | Mật khẩu |
|---------|-------|-----------|
| Owner | owner@hienhuu.vn | Owner@123 |
| Customer | customer@example.com | Customer@123 |
