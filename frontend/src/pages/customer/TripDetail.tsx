import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Bus, Users, Clock, Check, AlertCircle, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { tripApi, bookingApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'
import AIChat from '../../components/AIChat'

export default function TripDetail() {
  const { tripId } = useParams<{ tripId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [seatCount, setSeatCount] = useState(1)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

  const { data: trip, isLoading } = useQuery({
    queryKey: ['trip', tripId],
    queryFn: () => tripApi.getById(tripId!).then((res) => res.data),
    enabled: !!tripId,
  })

  const createBookingMutation = useMutation({
    mutationFn: (data: { trip_id: string; seat_count: number }) =>
      bookingApi.create(data).then((res) => res.data),
    onSuccess: (booking) => {
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] })
      setSuccess(true)
      setTimeout(() => {
        navigate(`/customer/bookings/${booking.id}`)
      }, 1500)
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Đặt vé thất bại')
    },
  })

  const handleBooking = () => {
    if (!trip) return
    if (seatCount > trip.available_seats) {
      setError(`Chỉ còn ${trip.available_seats} ghế trống`)
      return
    }
    setError('')
    createBookingMutation.mutate({ trip_id: trip.id, seat_count: seatCount })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-32 bg-neutral-100 rounded animate-pulse" />
        <div className="bg-white rounded-2xl p-6 shadow-card">
          <div className="h-64 bg-neutral-100 rounded-xl animate-pulse" />
        </div>
      </div>
    )
  }

  if (!trip) {
    return (
      <div className="card text-center py-16">
        <div className="empty-state-icon mx-auto">
          <Bus size={32} />
        </div>
        <p className="empty-state-title">Không tìm thấy chuyến xe</p>
        <button onClick={() => navigate('/customer/trips')} className="btn-primary mt-4">
          Quay lại tìm chuyến
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/customer/trips')}
        className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
      >
        <ArrowLeft size={20} />
        <span className="font-medium">Quay lại</span>
      </button>

      {/* Success state */}
      {success && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl p-8 shadow-elevated text-center max-w-md mx-4 animate-fade-in">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <Check className="text-green-600" size={32} />
            </div>
            <h2 className="text-2xl font-bold text-neutral-900 mb-2">Đặt vé thành công!</h2>
            <p className="text-neutral-500 mb-6">Đang chuyển đến trang thanh toán...</p>
            <div className="flex justify-center">
              <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
          </div>
        </div>
      )}

      {/* Trip header */}
      <div className="bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 rounded-2xl p-6 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full blur-3xl translate-x-1/2 -translate-y-1/2" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Bus className="text-white" size={28} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">{trip.route}</h1>
              <p className="text-primary-100 mt-1">{trip.origin} → {trip.destination}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
              <Clock className="mx-auto mb-2 text-primary-200" size={24} />
              <p className="text-sm text-primary-100">Giờ khởi hành</p>
              <p className="text-xl font-bold mt-1">{trip.departure_time}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
              <Clock className="mx-auto mb-2 text-primary-200" size={24} />
              <p className="text-sm text-primary-100">Giờ đến</p>
              <p className="text-xl font-bold mt-1">{trip.arrival_time}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
              <p className="text-sm text-primary-100 mb-2">Giá vé</p>
              <p className="text-2xl font-bold">{formatCurrency(trip.price)}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
              <p className="text-sm text-primary-100 mb-2">Ghế trống</p>
              <p className="text-2xl font-bold">{trip.available_seats}/{trip.total_seats}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Booking form */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-neutral-900">Đặt vé</h2>
            <p className="text-sm text-neutral-500 mt-1">Chọn số ghế và xác nhận đặt vé</p>
          </div>
          <button
            onClick={() => setChatOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-200 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <Sparkles size={16} className="text-primary-600" />
            <span className="text-sm font-medium text-primary-700">Hỏi AI</span>
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center gap-2 mb-4">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Seat selection */}
          <div className="bg-neutral-50 rounded-xl p-5">
            <label className="block text-sm font-medium text-neutral-700 mb-3">
              <Users className="inline mr-2" size={16} />
              Số ghế muốn đặt
            </label>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSeatCount(Math.max(1, seatCount - 1))}
                className="w-12 h-12 rounded-xl bg-white border border-neutral-200 font-bold text-xl hover:bg-neutral-100 transition-colors"
              >
                −
              </button>
              <input
                type="number"
                min="1"
                max={trip.available_seats}
                value={seatCount}
                onChange={(e) => setSeatCount(Math.max(1, Math.min(trip.available_seats, parseInt(e.target.value) || 1)))}
                className="w-20 text-center px-4 py-2 border border-neutral-200 rounded-xl font-semibold text-lg"
              />
              <button
                onClick={() => setSeatCount(Math.min(trip.available_seats, seatCount + 1))}
                className="w-12 h-12 rounded-xl bg-white border border-neutral-200 font-bold text-xl hover:bg-neutral-100 transition-colors"
              >
                +
              </button>
            </div>
            <p className="text-sm text-neutral-500 mt-3">
              Tối đa {trip.available_seats} ghế trống
            </p>
          </div>

          {/* Price summary */}
          <div className="bg-neutral-50 rounded-xl p-5">
            <h3 className="font-semibold text-neutral-900 mb-4">Tổng cộng</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-neutral-600">Giá mỗi ghế</span>
                <span className="font-medium">{formatCurrency(trip.price)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-neutral-600">Số ghế</span>
                <span className="font-medium">{seatCount}</span>
              </div>
              <div className="border-t border-neutral-200 pt-3 flex justify-between">
                <span className="font-semibold text-neutral-900">Tổng</span>
                <span className="text-2xl font-bold text-primary-600">{formatCurrency(trip.price * seatCount)}</span>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={handleBooking}
          disabled={createBookingMutation.isPending || trip.available_seats === 0}
          className="btn-primary w-full py-4 text-lg mt-6 disabled:opacity-50"
        >
          {createBookingMutation.isPending ? (
            <span className="flex items-center gap-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Đang xử lý...
            </span>
          ) : (
            `Đặt vé ngay - ${formatCurrency(trip.price * seatCount)}`
          )}
        </button>
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
