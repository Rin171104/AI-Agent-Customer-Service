# P-182 — AI20K Agent

Quy ước chung cho mọi AI coding tool làm việc trên repo này (Claude Code, Codex,
Cursor, Gemini CLI, Copilot, Antigravity). Đây là **nguồn sự thật duy nhất** —
các file rule riêng của từng tool chỉ nên trỏ về đây.

## Ngôn ngữ

- Trả lời, comment và docstring: **tiếng Việt**.
- Tên biến, hàm, class, file: **tiếng Anh**, snake_case theo PEP 8.

## Môi trường

- Máy dev chạy **Windows + PowerShell**. Lệnh trong `Makefile` viết theo POSIX
  (`find`, `rm -rf`) nên target `clean` không chạy được trực tiếp — chuyển thủ công.
- Dependency khai báo ở `requirements.txt`. Repo **không có** `pyproject.toml`
  lẫn `setup.py`, nên `pip install -e .` sẽ fail. Dùng:

  ```
  pip install -r requirements.txt
  ```

- `mypy` xuất hiện trong `Makefile` nhưng **không** có trong `requirements.txt`.
  Muốn chạy `make typecheck` phải cài thêm.

## Kiến trúc

Ba tầng, mỗi thư mục một trách nhiệm. Không phá vỡ ranh giới này:

| Thư mục | Trách nhiệm | Không được làm |
|---|---|---|
| `src/agents/` | Logic LangGraph | Không import gì từ `src/api/` |
| `src/api/` | HTTP, validate, mã lỗi | Không chứa logic nghiệp vụ |
| `src/models/` | Pydantic schema vào/ra | Không gọi LLM |
| `src/services/` | Tích hợp ngoài (LLM, DB) | Không biết gì về HTTP |
| `src/config.py` | Đọc `.env` qua Pydantic Settings | Không `os.getenv` rải rác nơi khác |

## Quy ước LangGraph

Đây là phần chiếm nhiều điểm nhất, làm sai rất khó sửa về sau:

- **Node** là hàm `async`, nhận `AgentState`, trả về **dict partial** — chỉ chứa
  field cần cập nhật. Không trả nguyên state; LangGraph tự merge.
- Field mới **phải khai báo trong `src/agents/state.py` trước**, rồi node mới dùng.
  `AgentState` có `total=False` nên mọi field đều optional.
- **Router function** (dùng cho `add_conditional_edges`) trả về **tên node** dạng
  string hoặc `END` — không trả dữ liệu.
- **Tool** đặt ở `src/agents/tools/`, gắn `@tool`. Docstring của tool chính là mô
  tả gửi cho LLM: viết rõ công dụng, tham số, giá trị trả về. Docstring mơ hồ =
  LLM gọi sai tool.
- Sau khi sửa `graph.py`, cập nhật sơ đồ mermaid ở `ARCHITECTURE.md` mục
  "3. AI Agent (LangGraph)".

## Ba thành phần mẫu chưa nối dây

Code mẫu trong template định nghĩa xong nhưng **chưa được import ở đâu cả**.
Đừng giả định chúng đang hoạt động:

| File | Tình trạng | Việc cần làm |
|---|---|---|
| `src/agents/tools/example_tool.py` | `search_knowledge`, `calculate` không ai gọi | Bind vào LLM rồi gắn vào node |
| `src/services/llm.py` | `get_llm()` không ai gọi | Gọi trong node để agent dùng LLM thật |
| `src/agents/nodes/example_node.py` | Chỉ nối f-string, còn 2 `# TODO` | Thay bằng logic thật |

Agent hiện tại **chưa gọi LLM lần nào** — nó chỉ trả về `f"Phân tích: {query}"`.

## Kiểm tra trước khi commit

```
ruff check src/ tests/
ruff format src/ tests/
pytest tests/ -v
```

Test dùng fixture `mock_llm` trong `tests/conftest.py` để không gọi OpenAI thật.
Viết test mới cho agent thì dùng fixture này, đừng gọi API thật trong test.

## Git

- Nhánh làm việc tách riêng, không commit thẳng vào `main`.
- Nhánh mới lần đầu push: `git push -u origin <tên-nhánh>`.
- Pre-push hook sẽ chạy script log rồi gửi lên grading server. Hook luôn `exit 0`
  nên không bao giờ chặn push — nếu push fail thì nguyên nhân nằm chỗ khác.

## Cấm

- ❌ Không commit `.env` (chứa `OPENAI_API_KEY`, `AI_LOG_API_KEY`).
- ❌ Không sửa hoặc xoá file trong `.ai-log/` — pre-push hook quản lý.
- ❌ Không dùng `git push --no-verify` để bỏ qua hook.
- ❌ Không sửa `scripts/` — hạ tầng logging của BTC.
- ❌ Không sửa `.claude/settings.json`, `.codex/hooks.json`, `.cursor/hooks.json`,
  `.gemini/settings.json`, `.github/hooks/hooks.json` — config hook của BTC.
- ❌ Không dùng `eval()` để tính biểu thức. Xem cách làm an toàn bằng `ast` ở
  `src/agents/tools/example_tool.py`.
- ❌ Chỉ thao tác trong chính thư mục này, không tự ý thay đổi các file, thư mục bên ngoài khác cho đến khi tôi cho phép

## Deliverables — file nào ứng với hạng mục nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Source Code | `src/` |
| 2 | README | `README.md` (copy từ `README_boilerplate.md`) |
| 3 | Architecture Diagram | `ARCHITECTURE.md`, `docs/architecture_diagram.md` |
| 4 | AI Logs & Observability | AI Trace trong SQLite + metrics/transcript JSONL + `.ai-log/` |
| 5 | Live URL | Deploy Render/Vercel |
| 6, 7 | Video + Pitch Deck | `presentation/` |
| 8 | Development Journal | `JOURNAL.md` — ghi theo **tuần** |
| 9 | Worklog | `WORKLOG.md` — ghi theo **ngày**, ai làm gì |
| 10 | Evaluation Evidence | `eval/results/report.md` |

Sửa code xong mà hạng mục tài liệu liên quan còn placeholder `[...]` thì nhắc user cập nhật.

## Lưu ý về README.md

`README.md` cần phản ánh đúng code và deliverable hiện tại; không dùng lại hướng
dẫn `pip install -e ".[dev]"` của template vì repo không có `pyproject.toml`/
`setup.py`. Remote thật là `AI20K-Build-Phase-Cohort-3`.
