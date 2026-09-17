# Database Schema

## Tables

### customers
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Customer name |
| phone | VARCHAR(20) | Phone number |
| email | VARCHAR(255) | Email address |
| created_at | TIMESTAMP | Creation time |

### routes
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| origin | VARCHAR(255) | Origin city |
| destination | VARCHAR(255) | Destination city |
| distance_km | INTEGER | Distance in km |

### buses
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| plate_number | VARCHAR(20) | License plate |
| seat_count | INTEGER | Number of seats |
| bus_type | VARCHAR(50) | Type of bus |

### trips
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| route_id | UUID | Foreign key to routes |
| bus_id | UUID | Foreign key to buses |
| departure_time | TIME | Departure time |
| arrival_time | TIME | Arrival time |
| price | INTEGER | Ticket price |
| status | VARCHAR(20) | active/cancelled |

### seats
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| trip_id | UUID | Foreign key to trips |
| seat_number | VARCHAR(10) | Seat identifier |
| status | VARCHAR(20) | available/booked/held |

### bookings
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| customer_id | UUID | Foreign key to customers |
| trip_id | UUID | Foreign key to trips |
| status | VARCHAR(20) | draft/confirmed/cancelled |
| total_amount | INTEGER | Total price |
| pickup_point | VARCHAR(255) | Pickup location |
| created_at | TIMESTAMP | Creation time |

### booking_seats
| Column | Type | Description |
|--------|------|-------------|
| booking_id | UUID | Foreign key to bookings |
| seat_id | UUID | Foreign key to seats |

### payments
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| booking_id | UUID | Foreign key to bookings |
| amount | INTEGER | Payment amount |
| method | VARCHAR(50) | Payment method |
| status | VARCHAR(20) | pending/paid/failed |
| transaction_id | VARCHAR(100) | External transaction ID |

### complaints
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| booking_id | UUID | Foreign key to bookings |
| customer_id | UUID | Foreign key to customers |
| type | VARCHAR(50) | Complaint type |
| description | TEXT | Complaint details |
| severity | VARCHAR(20) | low/medium/high |
| status | VARCHAR(20) | received/resolved/escalated |
| resolution | JSONB | Resolution details |

### knowledge_base (for RAG)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| content | TEXT | Document content |
| source | VARCHAR(255) | Source file |
| category | VARCHAR(50) | pricing/policies/schedules |
| embedding | VECTOR(1536) | pgvector embedding |

### agent_runs
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | Session identifier |
| user_id | UUID | User identifier |
| intent | VARCHAR(50) | Detected intent |
| status | VARCHAR(20) | running/completed/error |
| trace | JSONB | Execution trace |

## pgvector Setup

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Example index for similarity search
CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```
