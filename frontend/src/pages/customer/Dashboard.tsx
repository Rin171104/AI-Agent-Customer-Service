import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Bus,
  Ticket,
  MessageSquare,
  RefreshCcw,
  ArrowRight,
  Clock,
  Sparkles,
  Calendar,
  ChevronRight,
} from 'lucide-react'
import { useAuth } from '../../services/auth'
import { bookingApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import AIChat from '../../components/AIChat'
import { useState } from 'react'

export default function CustomerDashboard() {
  const { user } = useAuth()
  const [chatOpen, setChatOpen] = useState(false)

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => bookingApi.getMyBookings().then((res) => res.data),
  })

  const activeBookings = bookings?.filter((b) => b.status === 'CONFIRMED') || []
  const pendingPayments = bookings?.filter((b) => b.status === 'PENDING_PAYMENT') || []
  const upcomingBookings = activeBookings.slice(0, 2)

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 rounded-2xl p-6 text-white relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full blur-3xl translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-400 rounded-full blur-3xl -translate-x-1/2 translate-y-1/2" />
        </div>

        <div className="relative z-10">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-primary-100 text-sm font-medium">Chào mừng quay trở lại</p>
              <h1 className="text-2xl font-bold mt-1">{user?.name}!</h1>
              <p className="text-primary-100/80 text-sm mt-2">
                Hệ thống hỗ trợ bởi AI thông minh
              </p>
            </div>
            <button
              onClick={() => setChatOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-xl hover:bg-white/30 transition-colors"
            >
              <Sparkles size={18} />
              <span className="font-medium">Hỏi AI</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-primary-50 flex items-center justify-center">
              <Ticket className="text-primary-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{activeBookings.length}</p>
              <p className="text-sm text-neutral-500">Vé đang hoạt động</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-accent-50 flex items-center justify-center">
              <Bus className="text-accent-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{upcomingBookings.length}</p>
              <p className="text-sm text-neutral-500">Chuyến sắp tới</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-amber-50 flex items-center justify-center">
              <Clock className="text-amber-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{pendingPayments.length}</p>
              <p className="text-sm text-neutral-500">Chờ thanh toán</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-red-50 flex items-center justify-center">
              <MessageSquare className="text-red-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">0</p>
              <p className="text-sm text-neutral-500">Khiếu nại đang xử lý</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pending payments alert */}
      {pendingPayments.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
              <Clock className="text-amber-600" size={20} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900">Đơn hàng chờ thanh toán</h3>
              <p className="text-sm text-amber-700 mt-1">
                Bạn có {pendingPayments.length} đơn đặt vé chưa thanh toán
              </p>
              <div className="mt-3 space-y-2">
                {pendingPayments.map((booking) => (
                  <Link
                    key={booking.id}
                    to={`/customer/bookings/${booking.id}`}
                    className="flex items-center justify-between bg-white rounded-xl p-3 hover:shadow-soft transition-shadow"
                  >
                    <div>
                      <p className="font-medium text-neutral-900">{booking.booking_code}</p>
                      <p className="text-sm text-neutral-500">
                        {formatCurrency(booking.total_amount)} • {booking.seat_count} ghế
                      </p>
                    </div>
                    <span className="text-primary-600 font-medium text-sm flex items-center gap-1">
                      Thanh toán <ChevronRight size={16} />
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/customer/trips"
          className="group bg-white rounded-xl p-5 border border-neutral-100 hover:border-primary-200 hover:shadow-soft transition-all duration-200"
        >
          <div className="w-12 h-12 rounded-xl bg-primary-50 group-hover:bg-primary-100 flex items-center justify-center mb-4 transition-colors">
            <SearchIcon className="text-primary-600" size={24} />
          </div>
          <h3 className="font-semibold text-neutral-900">Tìm chuyến</h3>
          <p className="text-sm text-neutral-500 mt-1">Tìm và đặt vé xe</p>
        </Link>
        <Link
          to="/customer/bookings"
          className="group bg-white rounded-xl p-5 border border-neutral-100 hover:border-green-200 hover:shadow-soft transition-all duration-200"
        >
          <div className="w-12 h-12 rounded-xl bg-green-50 group-hover:bg-green-100 flex items-center justify-center mb-4 transition-colors">
            <Ticket className="text-green-600" size={24} />
          </div>
          <h3 className="font-semibold text-neutral-900">Xem vé</h3>
          <p className="text-sm text-neutral-500 mt-1">Quản lý đặt vé</p>
        </Link>
        <Link
          to="/customer/refunds"
          className="group bg-white rounded-xl p-5 border border-neutral-100 hover:border-purple-200 hover:shadow-soft transition-all duration-200"
        >
          <div className="w-12 h-12 rounded-xl bg-purple-50 group-hover:bg-purple-100 flex items-center justify-center mb-4 transition-colors">
            <RefreshCcw className="text-purple-600" size={24} />
          </div>
          <h3 className="font-semibold text-neutral-900">Hoàn tiền</h3>
          <p className="text-sm text-neutral-500 mt-1">Yêu cầu hoàn tiền</p>
        </Link>
        <button
          onClick={() => setChatOpen(true)}
          className="group bg-gradient-to-br from-primary-50 to-accent-50 rounded-xl p-5 border border-primary-100 hover:border-primary-200 hover:shadow-soft transition-all duration-200 text-left"
        >
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center mb-4">
            <Sparkles className="text-white" size={24} />
          </div>
          <h3 className="font-semibold text-neutral-900">Hỏi AI</h3>
          <p className="text-sm text-neutral-500 mt-1">Trợ lý 24/7</p>
        </button>
      </div>

      {/* Upcoming trips */}
      <div className="card">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-neutral-900">Chuyến sắp tới</h2>
          <Link
            to="/customer/bookings"
            className="text-sm text-primary-600 font-medium hover:text-primary-700 flex items-center gap-1"
          >
            Xem tất cả <ArrowRight size={16} />
          </Link>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-24 bg-neutral-100 rounded-xl" />
              </div>
            ))}
          </div>
        ) : upcomingBookings.length === 0 ? (
          <div className="empty-state py-12">
            <div className="empty-state-icon">
              <Bus size={32} />
            </div>
            <p className="empty-state-title">Chưa có chuyến nào</p>
            <p className="empty-state-description">Đặt vé ngay để trải nghiệm dịch vụ</p>
            <Link
              to="/customer/trips"
              className="btn-primary mt-4"
            >
              Tìm chuyến ngay
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {upcomingBookings.map((booking) => (
              <Link
                key={booking.id}
                to={`/customer/bookings/${booking.id}`}
                className="block bg-neutral-50 rounded-xl p-4 hover:bg-neutral-100 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0">
                      <Bus className="text-primary-600" size={20} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-neutral-900">{booking.booking_code}</span>
                        <span className={`badge ${getStatusColor(booking.status)}`}>
                          {getStatusText(booking.status)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-sm text-neutral-500">
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {formatDateTime(booking.created_at)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Ticket size={14} />
                          {booking.seat_count} ghế
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-primary-600">
                      {formatCurrency(booking.total_amount)}
                    </p>
                    <p className="text-xs text-neutral-500 mt-1">Xem chi tiết →</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* AI Chat Modal */}
      {chatOpen && (
        <div className="fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-black/30"
            onClick={() => setChatOpen(false)}
          />
          <div className="absolute bottom-0 right-0 w-full h-[calc(100vh-4rem)] lg:w-96 lg:h-[32rem] lg:rounded-t-2xl shadow-elevated">
            <AIChat
              context="customer"
              embedded
              onClose={() => setChatOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}

// Search icon component
function SearchIcon({ className, size = 24 }: { className?: string; size?: number }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  )
}
