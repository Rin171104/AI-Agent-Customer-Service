import { useQuery } from '@tanstack/react-query'
import { Ticket } from 'lucide-react'
import { bookingApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'

export default function OwnerBookings() {
  const { data: bookings, isLoading } = useQuery({
    queryKey: ['all-bookings'],
    queryFn: () => bookingApi.getAllBookings().then((res) => res.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Quản lý đặt vé</h1>
        <p className="text-gray-500 mt-1">Xem tất cả các đơn đặt vé</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-yellow-50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-yellow-600">
            {bookings?.filter((b) => b.status === 'PENDING_PAYMENT').length || 0}
          </p>
          <p className="text-sm text-yellow-700">Chờ thanh toán</p>
        </div>
        <div className="bg-green-50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-green-600">
            {bookings?.filter((b) => b.status === 'CONFIRMED').length || 0}
          </p>
          <p className="text-sm text-green-700">Đã xác nhận</p>
        </div>
        <div className="bg-red-50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-red-600">
            {bookings?.filter((b) => b.status === 'CANCELLED').length || 0}
          </p>
          <p className="text-sm text-red-700">Đã hủy</p>
        </div>
      </div>

      {/* Bookings List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : bookings?.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <Ticket className="mx-auto mb-3 text-gray-300" size={64} />
          <p className="text-lg">Chưa có đơn đặt vé nào</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã đặt</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày đặt</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Số ghế</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tổng tiền</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {bookings?.map((booking) => (
                <tr key={booking.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{booking.booking_code}</td>
                  <td className="px-6 py-4 text-gray-600">{formatDateTime(booking.created_at)}</td>
                  <td className="px-6 py-4 text-gray-600">{booking.seat_count}</td>
                  <td className="px-6 py-4 text-gray-600">{formatCurrency(booking.total_amount)}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                      {getStatusText(booking.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
