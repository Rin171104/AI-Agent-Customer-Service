import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Bus, CreditCard, Check, X, AlertCircle, Sparkles, Ticket } from 'lucide-react'
import { bookingApi, paymentApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import { useState } from 'react'
import AIChat from '../../components/AIChat'

export default function BookingDetail() {
  const { bookingId } = useParams<{ bookingId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [paymentSuccess, setPaymentSuccess] = useState(true)
  const [showCancelConfirm, setShowCancelConfirm] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

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
      setShowCancelConfirm(false)
    },
  })

  const handlePayment = () => {
    paymentMutation.mutate(paymentSuccess)
  }

  const handleCancel = () => {
    cancelMutation.mutate()
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-32 bg-neutral-100 rounded animate-pulse" />
        <div className="bg-white rounded-2xl p-6 shadow-card">
          <div className="h-96 bg-neutral-100 rounded-xl animate-pulse" />
        </div>
      </div>
    )
  }

  if (!booking) {
    return (
      <div className="card text-center py-16">
        <div className="empty-state-icon mx-auto">
          <Ticket size={32} />
        </div>
        <p className="empty-state-title">Không tìm thấy đơn đặt vé</p>
        <button onClick={() => navigate('/customer/bookings')} className="btn-primary mt-4">
          Quay lại danh sách vé
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/customer/bookings')}
        className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
      >
        <ArrowLeft size={20} />
        <span className="font-medium">Quay lại</span>
      </button>

      {/* Header */}
      <div className="bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 rounded-2xl p-6 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full blur-3xl translate-x-1/2 -translate-y-1/2" />
        </div>

        <div className="relative z-10 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 text-primary-100 text-sm mb-2">
              Mã đặt vé
            </div>
            <h1 className="text-3xl font-bold">{booking.booking_code}</h1>
            <p className="text-primary-100 mt-1">Đặt ngày {formatDateTime(booking.created_at)}</p>
          </div>
          <div className="text-right">
            <span className={`badge text-sm ${
              booking.status === 'CONFIRMED' ? 'bg-green-100 text-green-800 border-green-200' :
              booking.status === 'PENDING_PAYMENT' ? 'bg-amber-100 text-amber-800 border-amber-200' :
              'bg-red-100 text-red-800 border-red-200'
            }`}>
              {getStatusText(booking.status)}
            </span>
          </div>
        </div>
      </div>

      {/* Trip info */}
      <div className="card">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
            <Bus className="text-primary-600" size={20} />
          </div>
          <div>
            <h2 className="font-bold text-neutral-900">Thông tin chuyến xe</h2>
            <p className="text-sm text-neutral-500">{booking.trip.route}</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-neutral-50 rounded-xl p-5">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-3 h-3 rounded-full bg-green-500 mt-1.5" />
                <div>
                  <p className="text-sm text-neutral-500">Điểm đi</p>
                  <p className="font-semibold text-neutral-900">{booking.trip.origin}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-3 h-3 rounded-full bg-primary-500 mt-1.5" />
                <div>
                  <p className="text-sm text-neutral-500">Điểm đến</p>
                  <p className="font-semibold text-neutral-900">{booking.trip.destination}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-neutral-50 rounded-xl p-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-neutral-500">Giờ khởi hành</p>
                <p className="font-bold text-lg text-neutral-900">{booking.trip.departure_time}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-500">Giờ đến</p>
                <p className="font-bold text-lg text-neutral-900">{booking.trip.arrival_time}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Booking details */}
      <div className="card">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-accent-50 flex items-center justify-center">
            <Ticket className="text-accent-600" size={20} />
          </div>
          <div>
            <h2 className="font-bold text-neutral-900">Chi tiết đặt vé</h2>
            <p className="text-sm text-neutral-500">Thông tin vé của bạn</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-neutral-50 rounded-xl p-4">
            <p className="text-sm text-neutral-500">Số ghế</p>
            <p className="text-xl font-bold text-neutral-900">{booking.seat_count}</p>
          </div>
          <div className="bg-neutral-50 rounded-xl p-4">
            <p className="text-sm text-neutral-500">Giá mỗi ghế</p>
            <p className="text-xl font-bold text-neutral-900">{formatCurrency(booking.trip.price)}</p>
          </div>
          <div className="bg-neutral-50 rounded-xl p-4">
            <p className="text-sm text-neutral-500">Tổng tiền</p>
            <p className="text-xl font-bold text-primary-600">{formatCurrency(booking.total_amount)}</p>
          </div>
          <div className="bg-neutral-50 rounded-xl p-4">
            <p className="text-sm text-neutral-500">Trạng thái</p>
            <p className="text-xl font-bold text-neutral-900">{getStatusText(booking.status)}</p>
          </div>
        </div>
      </div>

      {/* Payment */}
      {booking.payment && (
        <div className="card">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
                <CreditCard className="text-purple-600" size={20} />
              </div>
              <div>
                <h2 className="font-bold text-neutral-900">Thanh toán</h2>
                <p className="text-sm text-neutral-500">Trạng thái thanh toán</p>
              </div>
            </div>
            <span className={`badge ${getStatusColor(booking.payment.status)}`}>
              {getStatusText(booking.payment.status)}
            </span>
          </div>

          <div className="bg-neutral-50 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-neutral-900">{formatCurrency(booking.payment.amount)}</p>
                <p className="text-sm text-neutral-500 mt-1">
                  Phương thức: {booking.payment.method}
                  {booking.payment.paid_at && ` • Ngày: ${formatDateTime(booking.payment.paid_at)}`}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="card">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-bold text-neutral-900">Hành động</h2>
          <button
            onClick={() => setChatOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-200 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <Sparkles size={16} className="text-primary-600" />
            <span className="text-sm font-medium text-primary-700">Hỏi AI</span>
          </button>
        </div>

        {booking.status === 'PENDING_PAYMENT' && (
          <div className="space-y-4">
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
              <AlertCircle className="text-amber-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="font-medium text-amber-900">Thanh toán đang chờ</p>
                <p className="text-sm text-amber-700 mt-1">Vui lòng thanh toán để xác nhận vé của bạn</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="paymentSuccess"
                checked={paymentSuccess}
                onChange={(e) => setPaymentSuccess(e.target.checked)}
                className="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="paymentSuccess" className="text-sm text-neutral-600">
                Mô phỏng thanh toán thành công (bỏ chọn để mô phỏng thất bại)
              </label>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handlePayment}
                disabled={paymentMutation.isPending}
                className="btn-success flex-1 py-3"
              >
                {paymentMutation.isPending ? (
                  <span className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Đang xử lý...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Check size={18} />
                    Thanh toán ngay
                  </span>
                )}
              </button>
              <button
                onClick={() => setShowCancelConfirm(true)}
                className="btn-danger px-6"
              >
                <X size={18} />
                Hủy đơn
              </button>
            </div>
          </div>
        )}

        {booking.status === 'CONFIRMED' && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
              <Check className="text-green-600" size={24} />
            </div>
            <div>
              <p className="font-bold text-green-900">Thanh toán thành công!</p>
              <p className="text-sm text-green-700 mt-1">Vé của bạn đã được xác nhận. Chúc bạn có chuyến đi vui vẻ!</p>
            </div>
          </div>
        )}

        {booking.status === 'CANCELLED' && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
              <X className="text-red-600" size={24} />
            </div>
            <div>
              <p className="font-bold text-red-900">Đơn đã bị hủy</p>
              <p className="text-sm text-red-700 mt-1">Đơn đặt vé này đã được hủy bỏ.</p>
            </div>
          </div>
        )}
      </div>

      {/* Cancel confirmation modal */}
      {showCancelConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4 shadow-elevated">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="text-red-600" size={32} />
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-2">Xác nhận hủy đơn?</h3>
              <p className="text-neutral-500 mb-6">
                Bạn có chắc muốn hủy đơn đặt vé này? Hành động này không thể hoàn tác.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => setShowCancelConfirm(false)}
                  className="btn-secondary flex-1"
                >
                  Không, giữ lại
                </button>
                <button
                  onClick={handleCancel}
                  disabled={cancelMutation.isPending}
                  className="btn-danger flex-1"
                >
                  {cancelMutation.isPending ? 'Đang hủy...' : 'Có, hủy đơn'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

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
