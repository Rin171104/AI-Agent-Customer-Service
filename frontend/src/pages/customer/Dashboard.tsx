import { useQuery } from '@tanstack/react-query'
import { Bus, Ticket, MessageSquare, RefreshCcw, Clock, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../services/auth'
import { bookingApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'

export default function CustomerDashboard() {
  const { user } = useAuth()

  const { data: bookings } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => bookingApi.getMyBookings().then((res) => res.data),
  })

  const upcomingBookings = bookings?.filter((b) => b.status === 'CONFIRMED').slice(0, 3) || []
  const pendingBookings = bookings?.filter((b) => b.status === 'PENDING_PAYMENT') || []

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold">Xin chào, {user?.name}!</h1>
        <p className="text-primary-100 mt-1">Chào mừng bạn đến với Hiền Hựu Bus</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link
          to="/customer/trips"
          className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center text-center"
        >
          <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mb-3">
            <Bus className="text-primary-600" size={24} />
          </div>
          <span className="font-medium text-gray-900">Tìm chuyến</span>
        </Link>
        <Link
          to="/customer/bookings"
          className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center text-center"
        >
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
            <Ticket className="text-green-600" size={24} />
          </div>
          <span className="font-medium text-gray-900">Đặt vé</span>
        </Link>
        <Link
          to="/customer/complaints"
          className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center text-center"
        >
          <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-3">
            <MessageSquare className="text-orange-600" size={24} />
          </div>
          <span className="font-medium text-gray-900">Khiếu nại</span>
        </Link>
        <Link
          to="/customer/refunds"
          className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center text-center"
        >
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
            <RefreshCcw className="text-purple-600" size={24} />
          </div>
          <span className="font-medium text-gray-900">Hoàn tiền</span>
        </Link>
      </div>

      {/* Pending Payments */}
      {pendingBookings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <div className="flex items-center gap-3 mb-3">
            <Clock className="text-yellow-600" size={20} />
            <h2 className="font-semibold text-yellow-800">Đơn hàng chờ thanh toán</h2>
          </div>
          <div className="space-y-2">
            {pendingBookings.map((booking) => (
              <div
                key={booking.id}
                className="bg-white rounded-lg p-3 flex items-center justify-between"
              >
                <div>
                  <p className="font-medium text-gray-900">{booking.booking_code}</p>
                  <p className="text-sm text-gray-500">
                    {formatCurrency(booking.total_amount)} - {booking.seat_count} ghế
                  </p>
                </div>
                <Link
                  to={`/customer/bookings/${booking.id}`}
                  className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  Thanh toán →
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Trips */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Chuyến sắp tới</h2>
          <Link to="/customer/bookings" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            Xem tất cả →
          </Link>
        </div>

        {upcomingBookings.length === 0 ? (
          <div className="bg-white rounded-xl p-8 text-center text-gray-500">
            <Bus className="mx-auto mb-3 text-gray-300" size={48} />
            <p>Chưa có chuyến nào được đặt</p>
            <Link
              to="/customer/trips"
              className="inline-flex items-center gap-2 mt-3 text-primary-600 hover:text-primary-700 font-medium"
            >
              Đặt vé ngay <ArrowRight size={16} />
            </Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {upcomingBookings.map((booking) => (
              <div key={booking.id} className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900">{booking.booking_code}</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                        {getStatusText(booking.status)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatDateTime(booking.created_at)} - {booking.seat_count} ghế
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{formatCurrency(booking.total_amount)}</p>
                    <Link
                      to={`/customer/bookings/${booking.id}`}
                      className="text-primary-600 hover:text-primary-700 text-sm"
                    >
                      Chi tiết →
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
