export const API_BASE_URL = '/api'

// Auth
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
  phone?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  name: string
  phone?: string
  role: 'CUSTOMER' | 'OWNER'
  created_at: string
}

// Trip
export interface Trip {
  id: string
  route: string
  origin: string
  destination: string
  departure_time: string
  arrival_time: string
  price: number
  total_seats: number
  available_seats: number
  status: 'ACTIVE' | 'CANCELLED'
  created_at: string
}

export interface CreateTripRequest {
  route: string
  origin: string
  destination: string
  departure_time: string
  arrival_time: string
  price: number
  total_seats: number
}

// Booking
export interface Booking {
  id: string
  booking_code: string
  user_id: string
  trip_id: string
  seat_count: number
  total_amount: number
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'CANCELLED'
  created_at: string
  updated_at: string
}

export interface BookingDetail extends Booking {
  trip: Trip
  payment?: Payment
}

export interface CreateBookingRequest {
  trip_id: string
  seat_count: number
}

// Payment
export interface Payment {
  id: string
  booking_id: string
  amount: number
  method: string
  status: 'PENDING' | 'PAID' | 'FAILED'
  paid_at?: string
  created_at: string
}

// Complaint
export interface Complaint {
  id: string
  complaint_code: string
  customer_id: string
  booking_id?: string
  type: 'WRONG_SEAT' | 'LATE' | 'DRIVER' | 'LOST_ITEM' | 'PAYMENT' | 'BOOKING_ERROR' | 'REFUND' | 'OTHER'
  description: string
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED'
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  owner_note?: string
  created_at: string
  updated_at: string
}

export interface ComplaintDetail extends Complaint {
  booking?: Booking
  refund_request?: Refund
}

export interface CreateComplaintRequest {
  booking_id?: string
  type: string
  description: string
  priority: string
}

export interface UpdateComplaintRequest {
  status?: string
  owner_note?: string
}

// Refund
export interface Refund {
  id: string
  refund_code: string
  complaint_id?: string
  booking_id: string
  amount: number
  bank_name: string
  account_number: string
  account_holder: string
  reason?: string
  status: 'REQUESTED' | 'WAITING_OWNER_APPROVAL' | 'APPROVED' | 'REJECTED' | 'REFUNDED'
  owner_note?: string
  created_at: string
  updated_at: string
}

export interface RefundDetail extends Refund {
  complaint?: Complaint
  booking?: Booking
}

export interface CreateRefundRequest {
  complaint_id?: string
  booking_id: string
  amount: number
  bank_name: string
  account_number: string
  account_holder: string
  reason?: string
}

// Audit Log
export interface AuditLog {
  id: string
  actor_type: 'CUSTOMER' | 'OWNER' | 'SYSTEM'
  actor_id?: string
  action: string
  entity_type: string
  entity_id?: string
  description?: string
  metadata?: Record<string, unknown>
  created_at: string
}

// Dashboard
export interface DashboardStats {
  total_trips: number
  today_trips: number
  total_bookings: number
  today_bookings: number
  revenue: number
  pending_payments: number
  open_complaints: number
  pending_refunds: number
}
