import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Ticket, Search } from 'lucide-react'
import { bookingApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'

export default function MyBookings() {
  const { data: bookings, isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => bookingApi.getMyBookings().then((res) => res.data),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Đặt vé của tôi</h1>
          <p className="text-gray-500 mt-1">Quản lý các đơn đặt vé của bạn</p>
        </div>
        <Link
          to="/customer/trips"
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Search size={18} />
          Tìm chuyến
        </Link>
      </div>

      {bookings?.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <Ticket className="mx-auto mb-4 text-gray-300" size={64} />
          <p className="text-lg">Chưa có đơn đặt vé nào</p>
          <p className="text-sm mt-2">Bắt đầu bằng việc tìm và đặt một chuyến xe</p>
          <Link
            to="/customer/trips"
            className="inline-flex items-center gap-2 mt-4 text-primary-600 hover:text-primary-700 font-medium"
          >
            Tìm chuyến xe ngay →
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {bookings?.map((booking) => (
            <Link
              key={booking.id}
              to={`/customer/bookings/${booking.id}`}
              className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow block"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-lg text-gray-900">{booking.booking_code}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                      {getStatusText(booking.status)}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>{formatDateTime(booking.created_at)}</span>
                    <span>•</span>
                    <span>{booking.seat_count} ghế</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-xl font-bold text-gray-900">{formatCurrency(booking.total_amount)}</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
