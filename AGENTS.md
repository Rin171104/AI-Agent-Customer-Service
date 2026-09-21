

Quy ước chung cho mọi AI coding tool làm việc trên repo này (Claude Code, Codex, Cursor, Gemini CLI, Copilot, Antigravity). Đây là **nguồn sự thật duy nhất** — các file rule riêng của từng tool chỉ nên trỏ về đây.

## Ngôn ngữ

- Trả lời, comment và docstring: **tiếng Việt**.
- Tên biến, hàm, class, file: **tiếng Anh**, snake_case theo PEP 8.

## Môi trường

- Máy dev chạy **Windows + PowerShell**.
- Backend: Python 3.11+ với FastAPI, chạy trong venv.
- Frontend: Node.js 18+ với React + Vite + TypeScript.
- Database: PostgreSQL 15 chạy trong Docker.

### Lệnh chạy

```powershell
# Database - khởi động PostgreSQL trong Docker
docker start hienhuu_postgres

# Backend
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Seed data (chạy 1 lần để tạo dữ liệu mẫu)
python seed_data.py

# Frontend (terminal mới)
cd frontend
npm run dev
```

## Kiến trúc

```
AI-Agent-Customer-Service/
├── backend/                    # FastAPI backend
│   ├── main.py                # Entry point
│   ├── seed_data.py           # Tạo dữ liệu mẫu
│   ├── requirements.txt       # Python dependencies
│   ├── run.bat               # Script chạy backend
│   └── src/
│       ├── api/routes/       # HTTP endpoints
│       ├── services/         # Business logic
│       ├── models/           # SQLAlchemy models
│       └── schemas.py       # Pydantic schemas
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/customer/  # Customer pages
│   │   ├── pages/owner/     # Owner pages
│   │   ├── components/      # Shared components
│   │   └── services/        # API client
│   └── run.bat             # Script chạy frontend
└── docker-compose.yml         # PostgreSQL
```

## Database

- PostgreSQL 15 chạy trong Docker (container `hienhuu_postgres`)
- Credentials: `hienhuu` / `hienhuu123`
- Database: `hienhuu_db`

## API Endpoints

| Module | Prefix | Mô tả |
|--------|--------|--------|
| auth | `/api/auth/*` | Đăng nhập, đăng ký |
| trips | `/api/trips/*` | CRUD chuyến xe |
| bookings | `/api/bookings/*` | Đặt vé, hủy vé |
| payments | `/api/payments/*` | Thanh toán |
| complaints | `/api/complaints/*` | Khiếu nại |
| refunds | `/api/refunds/*` | Hoàn tiền |
| audit | `/api/audit-logs/*` | Nhật ký |
| dashboard | `/api/dashboard/*` | Thống kê |

## Tài khoản demo

| Vai trò | Email | Mật khẩu |
|---------|-------|-----------|
| Owner | owner@hienhuu.vn | Owner@123 |
| Customer | customer@example.com | Customer@123 |

## Quy ước code

### Backend (Python)

- **Routes**: Xử lý HTTP request/response, validation cơ bản
- **Services**: Business logic, gọi database
- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic validation schemas

### Frontend (React/TypeScript)

- **Pages**: Route-level components
- **Components**: Reusable UI components
- **Services**: API client với Axios
- **Auth**: React Context cho authentication

## Kiểm tra trước khi commit

```powershell
# Backend - chạy Python linter
ruff check backend/src/

# Frontend - chạy TypeScript check
cd frontend
npx tsc --noEmit

# Build production
npm run build
```

## Git

- Nhánh làm việc tách riêng, không commit thẳng vào `main`.
- Nhánh mới lần đầu push: `git push -u origin <tên-nhánh>`.
- Pre-push hook sẽ chạy script log rồi gửi lên grading server. Hook luôn `exit 0` nên không bao giờ chặn push.

## Cấm

- ❌ Không commit `.env` (chứa database credentials).
- ❌ Không sửa hoặc xóa file trong `.ai-log/` — pre-push hook quản lý.
- ❌ Không dùng `git push --no-verify` để bỏ qua hook.
- ❌ Không sửa `scripts/` — hạ tầng logging của BTC.
- ❌ Không sửa `.claude/settings.json` — config hook của BTC.
- ❌ Chỉ thao tác trong chính thư mục này, không tự ý thay đổi các file, thư mục bên ngoài khác cho đến khi được cho phép.

## Deliverables — hạng mục tài liệu

| # | Hạng mục | File |
|---|---|---|
| 1 | Source Code | `backend/` và `frontend/` |
| 2 | README | `README.md` |
| 3 | API Documentation | Swagger tại `/docs` |
| 4 | Demo Video | Link video |
| 5 | Deployment URL | Cloudflare link |

Sửa code xong mà hạng mục tài liệu liên quan còn placeholder `[...]` thì nhắc user cập nhật.

## Lưu ý

- Backend API chạy tại `http://localhost:8000`
- Frontend chạy tại `http://localhost:5173`
- API docs tại `http://localhost:8000/docs`
- Docker container chạy PostgreSQL cần khởi động trước khi chạy backend
