import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Ticket, Calendar, Sparkles } from 'lucide-react'
import { bookingApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import AIChat from '../../components/AIChat'

type FilterType = 'all' | 'PENDING_PAYMENT' | 'CONFIRMED' | 'CANCELLED'

export default function OwnerBookings() {
  const [filter, setFilter] = useState<FilterType>('all')
  const [chatOpen, setChatOpen] = useState(false)

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['all-bookings', filter],
    queryFn: () =>
      bookingApi.getAllBookings(filter === 'all' ? undefined : { status: filter }).then((res) => res.data),
  })

  const filterTabs = [
    { key: 'all', label: 'Tất cả', count: bookings?.length || 0 },
    { key: 'PENDING_PAYMENT', label: 'Chờ thanh toán', count: bookings?.filter((b) => b.status === 'PENDING_PAYMENT').length || 0 },
    { key: 'CONFIRMED', label: 'Đã xác nhận', count: bookings?.filter((b) => b.status === 'CONFIRMED').length || 0 },
    { key: 'CANCELLED', label: 'Đã hủy', count: bookings?.filter((b) => b.status === 'CANCELLED').length || 0 },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Quản lý đặt vé</h1>
          <p className="text-neutral-500 mt-1">Xem và quản lý tất cả các đơn đặt vé</p>
        </div>
        <button
          onClick={() => setChatOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-xl hover:bg-primary-100 transition-colors"
        >
          <Sparkles size={18} className="text-primary-600" />
          <span className="font-medium text-primary-700">Hỏi AI</span>
        </button>
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
              <div className="h-20 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && bookings?.length === 0 && (
        <div className="bg-white rounded-2xl p-12 shadow-card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <Ticket size={32} />
            </div>
            <p className="empty-state-title">Không có đơn đặt vé nào</p>
            <p className="empty-state-description">
              {filter === 'all' ? 'Chưa có ai đặt vé' : 'Thử chọn bộ lọc khác'}
            </p>
          </div>
        </div>
      )}

      {/* Bookings list */}
      {!isLoading && bookings && bookings.length > 0 && (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="bg-white rounded-2xl p-5 shadow-card">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    booking.status === 'CONFIRMED' ? 'bg-green-50' :
                    booking.status === 'PENDING_PAYMENT' ? 'bg-amber-50' :
                    'bg-red-50'
                  }`}>
                    <Ticket className={
                      booking.status === 'CONFIRMED' ? 'text-green-600' :
                      booking.status === 'PENDING_PAYMENT' ? 'text-amber-600' :
                      'text-red-600'
                    } size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
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

                <div className="text-right">
                  <p className="text-xl font-bold text-primary-600">{formatCurrency(booking.total_amount)}</p>
                  <p className="text-sm text-neutral-500 mt-1">Tổng cộng</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* AI Chat Modal */}
      {chatOpen && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/30" onClick={() => setChatOpen(false)} />
          <div className="absolute bottom-0 right-0 w-full h-[calc(100vh-4rem)] lg:w-96 lg:h-[32rem] lg:rounded-t-2xl shadow-elevated">
            <AIChat context="owner" embedded onClose={() => setChatOpen(false)} />
          </div>
        </div>
      )}
    </div>
  )
}
