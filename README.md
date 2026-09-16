# AI Agent Customer Service & Ticket Booking Platform

> Multi-Agent AI System for Bus Ticket Booking & Customer Service Automation

## Overview

Hệ thống AI Agent tự động hóa hoạt động **chăm sóc khách hàng, đặt vé, thanh toán và xử lý khiếu nại** cho các nhà xe vừa và nhỏ.

Không giống chatbot thông thường chỉ trả lời câu hỏi, hệ thống này sử dụng kiến trúc **Multi-Agent** với khả năng thực hiện end-to-end business workflow.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                    (React / Next.js)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Chief Agent                             │
│                    (Orchestrator)                            │
│         Intent Detection → Task Delegation                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Booking     │    │  Complaint   │    │   Payment    │
│    Agent      │    │    Agent      │    │    Agent     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │              Capabilities                     │
        │  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
        │  │  RAG /  │  │  Tools  │  │  Database   │  │
        │  │Knowledge │  │         │  │(PostgreSQL) │  │
        │  │  Base   │  │         │  │  + pgvector │  │
        │  └─────────┘  └─────────┘  └─────────────┘  │
        └─────────────────────────────────────────────┘
                              │
                              ▼
              ┌─────────────────────────────┐
              │     Human-in-the-Loop       │
              │   (CSKH Approval Gate)     │
              └─────────────────────────────┘
```

## Agents

### Chief Agent
- Nhận yêu cầu từ khách hàng
- Xác định intent (booking, complaint, payment, FAQ)
- Delegate task cho Specialist Agent phù hợp
- Theo dõi và tổng hợp kết quả
- Kích hoạt Human-in-the-Loop khi cần

### Booking Agent
- Tìm kiếm chuyến xe
- Kiểm tra ghế trống
- Giữ ghế (hold_seat)
- Tạo booking draft
- Thu thập thông tin khách hàng

### Complaint Agent
- Tiếp nhận khiếu nại
- Phân loại mức độ nghiêm trọng
- Tra cứu booking liên quan
- Đề xuất hướng xử lý
- Escalate cho CSKH khi cần

### Payment Agent
- Tạo payment request
- Kiểm tra transaction
- Xác nhận thanh toán
- Cập nhật booking status

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ / FastAPI |
| Agent Framework | LangGraph |
| LLM | OpenAI / Anthropic / Local |
| Database | PostgreSQL 15+ |
| Vector DB | pgvector (PostgreSQL extension) |
| Frontend | React / Next.js |
| Auth | JWT |

## Features

- [x] Intent Detection & Agent Routing
- [x] Multi-Agent Handoff
- [x] Tool Calling (Booking, Payment, Complaint)
- [x] RAG / Knowledge Base
- [x] Human-in-the-Loop Approval
- [x] Shared State Management
- [x] Agent Run Trace / Audit Log
- [x] Live Agent Run Display

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ với pgvector extension
- Node.js 18+
- API Key cho LLM (OpenAI/Anthropic)

### 1. Clone & Setup Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Chỉnh sửa .env với database credentials và API keys
```

### 2. Setup Database

```sql
-- Tạo database
CREATE DATABASE ai_agent_cs;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tạo tables
-- (Xem backend/app/database/schema.sql)
```

### 3. Seed Knowledge Base

```bash
cd backend
python -m app.scripts.seed_knowledge
```

### 4. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 5. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at: http://localhost:3000

## Demo Conversation

```
Customer: "Tôi muốn đặt 2 vé Sài Gòn đi Đà Lạt ngày 20/09"

Chief Agent: → Intent = BOOKING → Delegate Booking Agent

Booking Agent: search_trip() → check_available_seats()
  → Còn ghế A05, A06, giá 250.000đ/vé

Chief Agent: "Chuyến 22:00 ngày 20/09 còn 2 ghế A05 và A06, 
              giá 250.000đ/vé. Bạn có muốn đặt không?"

Customer: "Có"

Booking Agent: hold_seat() → create_booking()

Chief Agent: → Handoff Payment Agent

Payment Agent: create_payment() → check_payment_status()
  → Payment Success

Chief Agent: → Booking CONFIRMED
```

## Project Structure

```
ai-agent-customer-service/
├── README.md                      # Tổng quan dự án, hướng dẫn cài đặt
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (không commit)
├── .gitignore
├── docker-compose.yml             # PostgreSQL + pgvector
│
├── src/
│   ├── agent/                     # Logic cốt lõi của agent
│   │   ├── __init__.py
│   │   ├── chief.py               # Chief Agent (Orchestrator)
│   │   ├── booking.py             # Booking Agent
│   │   ├── complaint.py           # Complaint Agent
│   │   ├── payment.py             # Payment Agent
│   │   ├── state.py               # Shared state management
│   │   ├── memory.py              # Conversation memory
│   │   └── executor.py            # Agent executor / runner
│   │
│   ├── tools/                     # Tools mà agent có thể sử dụng
│   │   ├── __init__.py
│   │   ├── booking_tools.py       # search_trip, hold_seat, create_booking
│   │   ├── payment_tools.py       # create_payment, check_payment
│   │   ├── complaint_tools.py     # create_complaint, update_complaint
│   │   └── search.py              # RAG search tool
│   │
│   ├── models/                    # LLM clients & embeddings
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   └── embeddings.py
│   │
│   ├── prompts/                   # System prompts
│   │   ├── __init__.py
│   │   ├── system_prompts.py
│   │   └── agent_prompts.py
│   │
│   ├── utils/                     # Helpers chung
│   │   ├── __init__.py
│   │   ├── config.py              # Load .env, config
│   │   ├── logger.py              # Logging
│   │   └── helpers.py
│   │
│   ├── api/                       # FastAPI routes
│   │   ├── __init__.py
│   │   ├── routes.py              # /chat, /bookings, /payments, /complaints
│   │   └── schemas.py             # Pydantic models
│
├── tests/                         # Unit & integration tests
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_api.py
│
├── data/                          # Knowledge base & seed data
│   ├── knowledge_base/            # Documents cho RAG
│   │   ├── pricing.md
│   │   ├── policies.md
│   │   └── schedules.md
│   └── examples.json              # Sample conversations
│
├── logs/                          # Application logs
│
├── frontend/                      # React/Next.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── app/
│   └── package.json
│
└── main.py                        # Entry point: uvicorn src.api:app
```

## API Endpoints

### Chat

```
POST /api/chat
Body: { "message": "...", "user_id": "..." }
Response: { "response": "...", "agent_trace": [...] }
```

### Booking

```
GET  /api/bookings
POST /api/bookings
GET  /api/bookings/{id}
PUT  /api/bookings/{id}
```

### Trips

```
GET  /api/trips?origin=...&destination=...&date=...
GET  /api/trips/{id}/seats
```

### Payments

```
POST /api/payments
GET  /api/payments/{id}
POST /api/payments/{id}/confirm
```

### Complaints

```
GET  /api/complaints
POST /api/complaints
GET  /api/complaints/{id}
PUT  /api/complaints/{id}
```

### Admin / Human-in-the-Loop

```
GET  /api/admin/pending-approvals
POST /api/admin/approvals/{id}
```

## Configuration

Xem `.env.example` cho các biến môi trường:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_agent_cs

# LLM
LLM_PROVIDER=openai  # hoặc anthropic, ollama
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Vector DB
EMBEDDING_MODEL=text-embedding-3-small

# App
SECRET_KEY=your-secret-key
DEBUG=true
```

## Documentation

- [PRD](PRD%20%E2%80%94%20AI%20Agent%20Customer%20Service%20&%20Ticket%20Booking%20Platform.md)

## License

MIT
