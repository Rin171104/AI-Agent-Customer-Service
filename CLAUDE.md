# P-182 — AI20K Agent

Quy ước chung của dự án (áp dụng cho mọi AI tool): @AGENTS.md

Phần dưới chỉ dành riêng cho Claude Code.

## Skill có sẵn
Chưa dùng, khi nào dùng tôi sẽ sửa

Skill nằm ở `.claude/skills/<tên>/SKILL.md`, được commit lên git nên cả team dùng chung.
Chú ý, chỉ thay đổi file trong thư mục này. Các thay đổi ở bên ngoài đều không được phép

## File không được sửa

`.claude/settings.json` chứa hook logging của BTC (`UserPromptSubmit`, `PostToolUse`,
`Stop`). Mọi tool call trong phiên đều được ghi vào `.ai-log/session.jsonl` rồi gửi
lên grading server khi `git push`. Không sửa file này.

Cấu hình cá nhân (permission, env riêng) đặt ở `.claude/settings.local.json` — và
nhớ thêm dòng đó vào `.gitignore` để không đè lên file của BTC.

## Lệnh trên Windows

Máy dev dùng PowerShell. Một số target trong `Makefile` viết theo POSIX nên không
chạy trực tiếp được — dùng lệnh gốc thay thế:

```powershell
# make run
uvicorn src.backend.main:app --reload --port 8000

# make test
pytest tests/ -v

# make check
ruff check src/backend/ tests/; ruff format src/backend/ tests/; pytest tests/ -v
```

## Deployment

Luôn khởi động lại service được thêm tính năng mới để cập nhật trên link production thông qua cloudflare.
