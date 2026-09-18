import axios from 'axios'
import type {
  LoginRequest, RegisterRequest, TokenResponse, User,
  Trip, CreateTripRequest,
  Booking, BookingDetail, CreateBookingRequest,
  Payment,
  Complaint, ComplaintDetail, CreateComplaintRequest, UpdateComplaintRequest,
  Refund, RefundDetail, CreateRefundRequest,
  AuditLog, DashboardStats
} from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export const authApi = {
  login: (data: LoginRequest) => api.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterRequest) => api.post<User>('/auth/register', data),
  me: () => api.get<User>('/auth/me'),
}

// Trips
export const tripApi = {
  getAll: (params?: { origin?: string; destination?: string }) =>
    api.get<Trip[]>('/trips', { params }),
  getById: (id: string) => api.get<Trip>(`/trips/${id}`),
  create: (data: CreateTripRequest) => api.post<Trip>('/trips', data),
  update: (id: string, data: Partial<CreateTripRequest>) => api.put<Trip>(`/trips/${id}`, data),
  delete: (id: string) => api.delete(`/trips/${id}`),
}

// Bookings
export const bookingApi = {
  getMyBookings: () => api.get<Booking[]>('/bookings'),
  getAllBookings: (params?: { status?: string }) => api.get<Booking[]>('/bookings/all', { params }),
  getById: (id: string) => api.get<BookingDetail>(`/bookings/${id}`),
  create: (data: CreateBookingRequest) => api.post<BookingDetail>('/bookings', data),
  cancel: (id: string) => api.patch<Booking>(`/bookings/${id}/cancel`),
}

// Payments
export const paymentApi = {
  getById: (id: string) => api.get<Payment>(`/payments/${id}`),
  pay: (id: string, success: boolean = true) => api.post<Payment>(`/payments/${id}/pay`, { success }),
}

// Complaints
export const complaintApi = {
  getMyComplaints: () => api.get<Complaint[]>('/complaints'),
  getAllComplaints: (params?: { status?: string; priority?: string }) =>
    api.get<ComplaintDetail[]>('/complaints/all', { params }),
  getById: (id: string) => api.get<ComplaintDetail>(`/complaints/${id}`),
  create: (data: CreateComplaintRequest) => api.post<Complaint>('/complaints', data),
  update: (id: string, data: UpdateComplaintRequest) => api.patch<Complaint>(`/complaints/${id}`, data),
  resolve: (id: string, note: string) => api.post<Complaint>(`/complaints/${id}/resolve?note=${encodeURIComponent(note)}`),
}

// Refunds
export const refundApi = {
  getMyRefunds: () => api.get<Refund[]>('/refunds'),
  getPendingRefunds: () => api.get<RefundDetail[]>('/refunds/pending'),
  getAllRefunds: () => api.get<RefundDetail[]>('/refunds/all'),
  getById: (id: string) => api.get<RefundDetail>(`/refunds/${id}`),
  create: (data: CreateRefundRequest) => api.post<Refund>('/refunds', data),
  approve: (id: string) => api.post<Refund>(`/refunds/${id}/approve`),
  reject: (id: string, note: string) => api.post<Refund>(`/refunds/${id}/reject`, { note }),
  markRefunded: (id: string) => api.post<Refund>(`/refunds/${id}/mark-refunded`),
}

// Audit
export const auditApi = {
  getLogs: (params?: { action?: string; entity_type?: string; limit?: number }) =>
    api.get<AuditLog[]>('/audit-logs', { params }),
}

// Dashboard
export const dashboardApi = {
  getStats: () => api.get<DashboardStats>('/dashboard/stats'),
}

export default api
