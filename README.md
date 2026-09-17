# AI Agent Platform for Hiền Hựu Bus Customer Service & Operations

> Multi-Agent AI System for Customer Service, Ticket Booking & Complaint Handling

---

## Table of Contents

1. [Overview](#overview)
2. [Problem](#problem)
3. [Why Multi-Agent?](#why-multi-agent)
4. [Product Flow](#product-flow)
5. [Architecture](#architecture)
6. [Agents](#agents)
   - [Chief Agent](#chief-agent)
   - [Booking Agent](#booking-agent)
   - [Complaint Agent](#complaint-agent)
   - [Payment Agent](#payment-agent)
7. [Agents vs Tools](#agents-vs-tools)
8. [Shared Capabilities](#shared-capabilities)
   - [RAG / Knowledge Base](#rag--knowledge-base)
   - [Shared State](#shared-state)
   - [Human-in-the-Loop](#human-in-the-loop)
9. [Core Workflows](#core-workflows)
   - [Booking Workflow](#booking-workflow)
   - [Complaint Workflow](#complaint-workflow)
   - [Payment Workflow](#payment-workflow)
10. [Business State](#business-state)
11. [Key Features](#key-features)
12. [Tech Stack](#tech-stack)
13. [Demo](#demo)
14. [Project Structure](#project-structure)
15. [API](#api)
16. [Configuration](#configuration)
17. [Quick Start](#quick-start)
18. [Roadmap](#roadmap)
19. [Documentation](#documentation)
20. [License](#license)

---

## Overview

This project is a **domain-specific AI Agent platform** designed for **Hiền Hựu Bus**.

The system automates customer service operations for the Hanoi ↔ Tà Xùa route, including:

| Domain | Description |
|--------|-------------|
| **Customer Service** | Answer questions about schedules, routes, vehicle types, pickup/drop-off |
| **Trip Information** | Provide current trip schedules and availability |
| **Ticket Booking** | Search trips, check seats, create bookings |
| **Payment Processing** | Process payments and confirm bookings |
| **Complaint Handling** | Receive, classify, and resolve customer complaints |

### What This Is NOT

This is **not just a conversational chatbot**.

```
Customer Request
        ↓
Chief Agent (Orchestrator)
        ↓
Specialist Agent
        ↓
Tools / Knowledge Base / Database
        ↓
Validation
        ↓
Human Approval (when required)
        ↓
Business Action
        ↓
Updated State
```

The system executes **real business workflows** — not just generating text responses.

---

## Problem

### Customer Service Challenges

| Challenge | Impact |
|-----------|--------|
| Repeated questions about schedules, prices, pickup points | Staff time spent on manual lookups |
| Customer requests arriving through multiple channels | Inconsistent responses |
| Manual information retrieval | Slow response times, potential errors |

### Ticket Booking Challenges

| Challenge | Impact |
|-----------|--------|
| Collecting multiple pieces of information | Multi-step manual process |
| Checking trip availability and seats | Manual coordination required |
| Manual booking entry | Risk of incorrect information |

### Complaint Handling Challenges

| Challenge | Impact |
|-----------|--------|
| Various complaint types (pickup, booking, seat, service) | Requires context retrieval |
| Need to verify booking before resolution | Multiple system lookups |
| Sensitive cases requiring human judgment | Cannot be fully automated |

---

## Why Multi-Agent?

| Concern | Single Agent | Multi-Agent |
|---------|--------------|-------------|
| **Domain separation** | Mixed logic | Specialist agents per business domain |
| **Booking vs Complaint** | Overlapping rules | Clear responsibility boundaries |
| **Payment flow** | Confused with other intents | Downstream specialist |
| **Scalability** | Complex when adding features | Add agents without rewriting |
| **Maintainability** | Prompt engineering bottlenecks | Isolated agent responsibilities |
| **Controllability** | Hard to audit | Clear delegation & validation |

**The goal is not to create many agents, but to separate distinct business responsibilities.**

- **Chief Agent** handles orchestration (understand, plan, route, validate)
- **Booking Agent** handles ticket booking operations
- **Complaint Agent** handles customer complaints
- **Payment Agent** handles payment processing (downstream)

---

## Product Flow

```
Understand
    ↓
Plan
    ↓
Delegate
    ↓
Execute
    ↓
Validate
    ↓
Human Approval (when required)
    ↓
Act
    ↓
Update Business State
```

Each step:

| Step | Description |
|------|-------------|
| **1. Understand** | Parse intent and extract entities from request |
| **2. Plan** | Determine required specialist agent(s) |
| **3. Delegate** | Route to appropriate agent with context |
| **4. Execute** | Agent uses tools, RAG, database |
| **5. Validate** | Chief Agent validates results |
| **6. Human Approval** | Triggered for high-risk actions |
| **7. Act** | Execute business action |
| **8. Update State** | Persist changes to database |

---

## Architecture

```mermaid
flowchart TD
    U[Customer] --> C[Chief Agent]

    C --> B[Booking Agent]
    C --> CO[Complaint Agent]
    C --> P[Payment Agent]

    B --> BT[Booking Tools]
    CO --> CT[Complaint Tools]
    P --> PT[Payment Tools]

    B --> DB[(PostgreSQL)]
    CO --> DB
    P --> DB

    CO --> R[RAG / Knowledge Base<br/>Hiền Hựu Service Info]

    C --> V[Validation]

    V --> H{Human Approval<br/>Required?}

    H -->|No| A[Business Action]
    H -->|Yes| HITL[CSKH Approval]

    HITL --> A
    A --> S[Updated Business State]
```

---

## Agents

### Chief Agent

**Orchestrator** — coordinates the entire workflow.

| Responsibility | Description |
|----------------|-------------|
| Understand request | Accept customer input |
| Detect intent | Identify booking, complaint, payment, FAQ |
| Delegate task | Route to appropriate Specialist Agent |
| Coordinate workflow | Manage multi-step processes |
| Validate results | Check specialist agent outputs |
| Trigger HITL | Activate human approval when required |
| Produce final response | Communicate result to customer |

### Booking Agent

**Domain: Hiền Hựu Ticket Booking**

| Capability | Description |
|------------|-------------|
| Search available trips | Find trips by route and date |
| Check seat availability | Show available seats for selected trip |
| Select vehicle type | Display Limousine, Cabin options |
| Collect customer information | Gather passenger details |
| Create booking draft | Prepare booking for confirmation |
| Hold seat | Temporarily reserve seat (if supported) |

### Complaint Agent

**Domain: Customer Complaints**

| Capability | Description |
|------------|-------------|
| Receive complaint | Accept and classify issue |
| Identify complaint type | Pickup issue, booking issue, seat/cabin issue, service issue |
| Retrieve related booking | Fetch booking context |
| Analyze the issue | Assess severity and impact |
| Recommend resolution | Suggest appropriate action |
| Escalate | Route to CSKH when required |

### Payment Agent

**Domain: Payment Processing**

Payment Agent is a **downstream specialist** activated after customer confirms booking.

```
Customer Booking Request
        ↓
Booking Agent
        ↓
Booking Draft Created
        ↓
Customer Confirms
        ↓
Payment Agent Activated
        ↓
Payment Processing
        ↓
Booking Confirmed
```

---

## Agents vs Tools

### Agents

Responsible for:
- **Reasoning** and decision-making
- **Delegation** and coordination
- **Workflow** decisions
- **Domain-specific** task handling

### Tools

Responsible for **deterministic operations**:

| Domain | Operations |
|--------|------------|
| **Booking Tools** | `search_trip`, `check_seat`, `hold_seat`, `create_booking`, `get_booking` |
| **Payment Tools** | `create_payment`, `check_payment`, `confirm_payment` |
| **Complaint Tools** | `create_complaint`, `get_complaint`, `update_complaint` |
| **Search Tool** | Semantic search over knowledge base |

Tools execute actions; they do not reason.

---

## Shared Capabilities

### RAG / Knowledge Base

**RAG is a shared capability, NOT an agent.**

Used by agents to retrieve approved information about Hiền Hựu services:

| Information Type | Example |
|-----------------|---------|
| Vehicle types | Limousine, Cabin |
| Service areas | Hanoi ↔ Tà Xùa route |
| Pickup/drop-off | Pickup points, drop-off locations |
| General booking info | Booking process, requirements |
| Policies | Terms of service, complaint policies |

**Important:** RAG provides knowledge retrieval; it does not replace transactional tools.

```
"What time does the bus leave?"
→ Knowledge Base / Trip Data Tool

"I want to book 2 tickets."
→ Booking Agent + Booking Tools
```

### Shared State

Agents share context throughout a workflow:

```json
{
  "user_id": "...",
  "intent": "booking",
  "origin": "Hanoi",
  "destination": "Ta Xua",
  "travel_date": "2026-09-20",
  "quantity": 2,
  "trip_id": "...",
  "customer_name": "...",
  "phone": "...",
  "booking_id": "...",
  "booking_status": "PENDING_PAYMENT",
  "payment_status": "UNPAID",
  "requires_human_approval": false
}
```

### Human-in-the-Loop

**HITL is a conditional control gate** for sensitive or high-risk actions.

Not every workflow requires human approval.

```mermaid
flowchart TD
    A[Agent Decision] --> Q{Approval Required?}

    Q -->|No| B[Execute Action]
    Q -->|Yes| C[CSKH Review]
    C --> D{Approved?}

    D -->|Yes| B
    D -->|No| E[Reject / Modify]
```

| Trigger | Example |
|---------|---------|
| Refund requests | Customer asks for refund |
| Booking cancellation | Special cancellation requests |
| Complaint escalation | High-severity complaints |
| Out-of-policy actions | Unusual customer requests |

---

## Core Workflows

### Booking Workflow

```mermaid
flowchart LR
    A[Customer] -->|Request| B[Chief]
    B -->|Delegate| C[Booking Agent]
    C --> D[Search Trip]
    D --> E[Check Availability]
    E --> F[Show Options]
    F --> A
    A -->|Select| G[Collect Info]
    G --> H[Create Booking Draft]
    H --> I[Customer Confirm]
    I --> J[Payment Agent]
    J --> K[Process Payment]
    K --> L{Success?}
    L -->|Yes| M[Confirm Booking]
    L -->|No| N[Retry]
    M --> O[Business State Updated]
```

### Complaint Workflow

```mermaid
flowchart TD
    A[Customer] -->|Complaint| B[Chief]
    B -->|Delegate| C[Complaint Agent]
    C --> D[Retrieve Booking]
    D --> E[Analyze Issue]
    E --> F{Type?}
    F -->|Simple| G[Auto Resolution]
    F -->|Complex| H[CSKH Review]
    G --> I[Update State]
    H --> J{Approved?}
    J -->|Yes| K[Execute Resolution]
    J -->|No| L[Reject]
    K --> I
    I --> M[Notify Customer]
```

### Payment Workflow

Payment is a **downstream workflow** triggered after customer confirms booking:

```
Booking Draft Created
        ↓
Customer Confirms
        ↓
Payment Agent Activated
        ↓
Payment Processing
        ↓
Verify Payment
        ↓
Confirm Booking → CONFIRMED
```

---

## Business State

The agents operate on business state through controlled tools instead of only generating text.

| Entity | Description |
|--------|-------------|
| **Customer** | Passenger information |
| **Route** | Origin-destination pairs (e.g., Hanoi ↔ Tà Xùa) |
| **Trip** | Scheduled journey with time, vehicle type |
| **Vehicle** | Bus type (Limousine, Cabin) |
| **Seat** | Individual seat with status |
| **Booking** | Ticket reservation record |
| **Payment** | Transaction record |
| **Complaint** | Customer issue record |

---

## Key Features

| Capability | Description |
|------------|-------------|
| Intent Detection | Routes requests to appropriate workflows |
| Multi-Agent Handoff | Enables specialist delegation |
| Tool Calling | Executes business operations |
| RAG | Retrieves approved Hiền Hựu service information |
| HITL | Controls sensitive actions |
| Shared State | Maintains workflow context |
| Agent Run Trace | Tracks execution for audit |

---

## Tech Stack

### Backend

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Agent Framework | LangGraph |

### AI

| Component | Technology |
|-----------|------------|
| LLM | OpenAI GPT-4 / Anthropic Claude |
| Embeddings | OpenAI Embeddings |
| RAG | Semantic search with vector database |

### Database

| Component | Technology |
|-----------|------------|
| Relational | PostgreSQL 15+ |
| Vector | pgvector |

### Frontend

| Component | Technology |
|-----------|------------|
| Runtime | Node.js |
| Framework | Express.js / React |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Container | Docker |
| Database | Docker Compose (PostgreSQL + pgvector) |

---

## Demo

```
Customer:
"I want to book 2 tickets from Hanoi to Ta Xua."

Chief Agent:
→ Detects: booking intent
→ Entities: origin=Hanoi, destination=Ta Xua, quantity=2
→ Delegates to Booking Agent

Booking Agent:
→ search_trip(origin="Hanoi", destination="Ta Xua")
→ check_available_seats(trip_id="...")
→ Returns available trips and seats

Chief Agent:
→ "Found available trips for Hanoi to Ta Xua.
   Would you like to see the options?"

Customer:
"Yes, show me."

Booking Agent:
→ Returns trip options with vehicle types and schedules

Customer:
"I want to book the first one."

Booking Agent:
→ hold_seat(trip_id="...", seats=["A1", "A2"])
→ create_booking(customer_info={...})
→ Returns booking draft

Chief Agent:
→ "Booking created. Total: [amount]. Proceed to payment?"

Customer:
"Confirm."

Chief Agent:
→ Delegates to Payment Agent

Payment Agent:
→ create_payment(booking_id="...")
→ check_payment_status(booking_id="...")
→ Returns payment status

Chief Agent:
→ "Payment received. Booking confirmed!"

Final State:
→ booking_id: [id]
→ booking_status: CONFIRMED
→ payment_status: PAID
→ seats: [selected seats]
```

---

## Project Structure

```
ai-agent-customer-service/
│
├── backend/
│   ├── src/
│   │   ├── agent/
│   │   │   ├── chief.py           # Chief Agent (Orchestrator)
│   │   │   ├── booking.py         # Booking Agent
│   │   │   ├── complaint.py       # Complaint Agent
│   │   │   ├── payment.py         # Payment Agent
│   │   │   ├── state.py           # Shared state management
│   │   │   └── executor.py        # Agent executor
│   │   │
│   │   ├── tools/
│   │   │   ├── booking_tools.py   # search_trip, check_seat, hold_seat, create_booking
│   │   │   ├── payment_tools.py   # create_payment, check_payment, confirm_payment
│   │   │   ├── complaint_tools.py # create_complaint, get_complaint, update_complaint
│   │   │   └── search.py          # RAG semantic search
│   │   │
│   │   ├── models/
│   │   │   ├── llm_client.py      # LLM provider abstraction (OpenAI, Anthropic)
│   │   │   └── embeddings.py       # Text embeddings
│   │   │
│   │   ├── prompts/
│   │   │   ├── chief_prompts.py   # Chief Agent prompts
│   │   │   └── agent_prompts.py    # Specialist Agent prompts
│   │   │
│   │   ├── utils/
│   │   │   ├── config.py           # Environment settings
│   │   │   └── logger.py           # Structured logging
│   │   │
│   │   └── api/
│   │       ├── routes.py           # FastAPI endpoints
│   │       └── schemas.py           # Pydantic models
│   │
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py                     # Entry: uvicorn main:app --reload
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js app router
│   │   │   ├── page.tsx           # Home page
│   │   │   ├── layout.tsx         # Root layout
│   │   │   └── globals.css         # Global styles
│   │   ├── components/             # Reusable UI components
│   │   ├── features/               # Feature modules
│   │   │   ├── chat/              # Chat interface
│   │   │   ├── booking/           # Booking UI
│   │   │   └── complaints/        # Complaints UI
│   │   ├── services/              # API services
│   │   └── utils/                 # Helpers
│   │
│   ├── package.json                # Dependencies
│   ├── tsconfig.json               # TypeScript config
│   ├── next.config.js              # Next.js config
│   ├── tailwind.config.js          # Tailwind CSS
│   ├── postcss.config.js           # PostCSS
│   └── .env.example
│
├── data/
│   └── knowledge-base/            # RAG documents
│       ├── pricing.md
│       ├── policies.md
│       └── schedules.md
│
├── docs/
│   └── database-schema.md          # PostgreSQL schema
│
├── docker-compose.yml               # PostgreSQL + pgvector
├── .gitignore
├── README.md
└── CLAUDE.md

---

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, receive agent response |
| `/api/bookings` | GET, POST | List or create bookings |
| `/api/bookings/{id}` | GET, PUT | Get or update booking |
| `/api/trips` | GET | Search trips by route and date |
| `/api/payments` | POST | Create payment |
| `/api/payments/{id}/confirm` | POST | Confirm payment |
| `/api/complaints` | GET, POST | List or create complaints |
| `/api/admin/pending-approvals` | GET | Get pending HITL approvals |

---

## Configuration

Environment variables (see `backend/.env.example`):

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_agent_cs

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small

# App
SECRET_KEY=your-secret-key
DEBUG=true
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector
- Docker (for database)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Start server
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

App available at: http://localhost:3000

### Database (Docker)

```bash
docker-compose up -d
```

---

## Roadmap

### Phase 1 — MVP

- [ ] Core Agent architecture (Chief + Specialist Agents)
- [ ] Booking workflow (search → book → pay → confirm)
- [ ] Complaint workflow (receive → classify → resolve)
- [ ] Basic RAG for Hiền Hựu service information
- [ ] Human-in-the-Loop approval mechanism
- [ ] API backend

### Phase 2 — Customer Service

- [ ] Multi-channel support
- [ ] Conversation memory
- [ ] Customer history

### Phase 3 — Operations

- [ ] Fleet/Trip Management
- [ ] Revenue Analytics
- [ ] Reporting Dashboard

---

## Documentation

- [PRD](PRD%20%E2%80%94%20AI%20Agent%20Customer%20Service%20&%20Ticket%20Booking%20Platform.md) — Detailed product requirements

---

## Data Accuracy Notice

> Schedule, pricing, seat availability and pickup/drop-off information may change over time. The AI system should retrieve transactional information from the current business data source or tools rather than relying solely on static knowledge.

---

## License

MIT
