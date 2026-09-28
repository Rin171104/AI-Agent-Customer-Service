import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Ticket, Search, Calendar } from 'lucide-react'
import { bookingApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'

type FilterType = 'all' | 'PENDING_PAYMENT' | 'CONFIRMED' | 'CANCELLED'

export default function MyBookings() {
  const [filter, setFilter] = useState<FilterType>('all')

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => bookingApi.getMyBookings().then((res) => res.data),
  })

  const filteredBookings = bookings?.filter((b) => filter === 'all' || b.status === filter) || []

  const filterTabs = [
    { key: 'all', label: 'Tất cả', count: bookings?.length || 0 },
    { key: 'PENDING_PAYMENT', label: 'Chờ thanh toán', count: bookings?.filter((b) => b.status === 'PENDING_PAYMENT').length || 0 },
    { key: 'CONFIRMED', label: 'Đã xác nhận', count: bookings?.filter((b) => b.status === 'CONFIRMED').length || 0 },
    { key: 'CANCELLED', label: 'Đã hủy', count: bookings?.filter((b) => b.status === 'CANCELLED').length || 0 },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Vé của tôi</h1>
          <p className="text-neutral-500 mt-1">Quản lý các đơn đặt vé của bạn</p>
        </div>
        <Link to="/customer/trips" className="btn-primary">
          <Search size={18} />
          Tìm chuyến
        </Link>
      </div>

      {/* Filter tabs */}
      <div className="bg-white rounded-xl p-1.5 shadow-card inline-flex">
        {filterTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key as FilterType)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'bg-primary-600 text-white'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            {tab.label}
            <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
              filter === tab.key ? 'bg-white/20' : 'bg-neutral-100'
            }`}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-card animate-pulse">
              <div className="h-16 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && filteredBookings.length === 0 && (
        <div className="bg-white rounded-2xl p-12 shadow-card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <Ticket size={32} />
            </div>
            <p className="empty-state-title">
              {filter === 'all' ? 'Chưa có đơn đặt vé nào' : 'Không có vé nào'}
            </p>
            <p className="empty-state-description">
              {filter === 'all'
                ? 'Bắt đầu bằng việc tìm và đặt một chuyến xe'
                : 'Thử chọn bộ lọc khác'}
            </p>
            {filter === 'all' && (
              <Link to="/customer/trips" className="btn-primary mt-4">
                Tìm chuyến xe ngay
              </Link>
            )}
          </div>
        </div>
      )}

      {/* Booking list */}
      {!isLoading && filteredBookings.length > 0 && (
        <div className="space-y-4">
          {filteredBookings.map((booking) => (
            <Link
              key={booking.id}
              to={`/customer/bookings/${booking.id}`}
              className="block bg-white rounded-2xl p-5 shadow-card hover:shadow-elevated transition-all duration-200 group"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0 group-hover:bg-primary-100 transition-colors">
                    <Ticket className="text-primary-600" size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="font-bold text-lg text-neutral-900">{booking.booking_code}</span>
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

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-xl font-bold text-neutral-900">{formatCurrency(booking.total_amount)}</p>
                    <p className="text-sm text-neutral-500">Tổng cộng</p>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center group-hover:bg-primary-100 transition-colors">
                    <span className="text-neutral-400 group-hover:text-primary-600">→</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
