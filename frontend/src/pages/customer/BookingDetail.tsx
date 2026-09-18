import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Bus, Calendar, CreditCard, Check, X } from 'lucide-react'
import { bookingApi, paymentApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import { useState } from 'react'

export default function BookingDetail() {
  const { bookingId } = useParams<{ bookingId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [paymentSuccess, setPaymentSuccess] = useState(true)

  const { data: booking, isLoading } = useQuery({
    queryKey: ['booking', bookingId],
    queryFn: () => bookingApi.getById(bookingId!).then((res) => res.data),
    enabled: !!bookingId,
  })

  const paymentMutation = useMutation({
    mutationFn: (success: boolean) => {
      if (!booking?.payment) throw new Error('No payment')
      return paymentApi.pay(booking.payment.id, success).then((res) => res.data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => {
      if (!bookingId) throw new Error('No booking')
      return bookingApi.cancel(bookingId).then((res) => res.data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] })
    },
  })

  const handlePayment = () => {
    paymentMutation.mutate(paymentSuccess)
  }

  const handleCancel = () => {
    if (confirm('Bạn có chắc muốn hủy đơn đặt vé này?')) {
      cancelMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  if (!booking) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Không tìm thấy đơn đặt vé</p>
        <button onClick={() => navigate('/customer/bookings')} className="mt-4 text-primary-600 hover:text-primary-700">
          Quay lại
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/customer/bookings')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft size={20} />
        Quay lại
      </button>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{booking.booking_code}</h1>
              <p className="text-gray-500 mt-1">Đặt vé ngày {formatDateTime(booking.created_at)}</p>
            </div>
            <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(booking.status)}`}>
              {getStatusText(booking.status)}
            </span>
          </div>
        </div>

        {/* Trip Info */}
        <div className="p-6 border-b bg-gray-50">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Bus size={20} />
            Thông tin chuyến xe
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div>
                  <p className="text-sm text-gray-500">Tuyến</p>
                  <p className="font-semibold">{booking.trip.route}</p>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="text-sm">{booking.trip.origin}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full" />
                  <span className="text-sm">{booking.trip.destination}</span>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Giờ khởi hành</p>
                  <p className="font-semibold">{booking.trip.departure_time}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Giờ đến</p>
                  <p className="font-semibold">{booking.trip.arrival_time}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Booking Details */}
        <div className="p-6 border-b">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Calendar size={20} />
            Chi tiết đặt vé
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Số ghế</p>
              <p className="font-semibold">{booking.seat_count}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Giá mỗi ghế</p>
              <p className="font-semibold">{formatCurrency(booking.trip.price)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Tổng tiền</p>
              <p className="font-bold text-primary-600 text-lg">{formatCurrency(booking.total_amount)}</p>
            </div>
          </div>
        </div>

        {/* Payment */}
        {booking.payment && (
          <div className="p-6 border-b">
            <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CreditCard size={20} />
              Thanh toán
            </h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{formatCurrency(booking.payment.amount)}</p>
                  <p className="text-sm text-gray-500">
                    Phương thức: {booking.payment.method}
                    {booking.payment.paid_at && ` • Ngày: ${formatDateTime(booking.payment.paid_at)}`}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(booking.payment.status)}`}>
                  {getStatusText(booking.payment.status)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="p-6 bg-gray-50">
          {booking.status === 'PENDING_PAYMENT' && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="paymentSuccess"
                  checked={paymentSuccess}
                  onChange={(e) => setPaymentSuccess(e.target.checked)}
                  className="w-4 h-4"
                />
                <label htmlFor="paymentSuccess" className="text-sm text-gray-600">
                  Mô phỏng thanh toán thành công (bỏ chọn để mô phỏng thất bại)
                </label>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={handlePayment}
                  disabled={paymentMutation.isPending}
                  className="flex-1 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {paymentMutation.isPending ? 'Đang xử lý...' : (
                    <>
                      <Check size={20} />
                      Thanh toán
                    </>
                  )}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={cancelMutation.isPending}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {cancelMutation.isPending ? 'Đang hủy...' : (
                    <>
                      <X size={20} />
                      Hủy đơn
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {booking.status === 'CONFIRMED' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
              <Check className="text-green-600" size={24} />
              <div>
                <p className="font-semibold text-green-800">Thanh toán thành công!</p>
                <p className="text-sm text-green-600">Vé của bạn đã được xác nhận</p>
              </div>
            </div>
          )}

          {booking.status === 'CANCELLED' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
              <X className="text-red-600" size={24} />
              <div>
                <p className="font-semibold text-red-800">Đơn đã bị hủy</p>
                <p className="text-sm text-red-600">Đơn đặt vé này đã được hủy bỏ</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
