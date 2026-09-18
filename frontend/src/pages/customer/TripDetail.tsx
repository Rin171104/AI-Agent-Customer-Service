import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Bus, Users } from 'lucide-react'
import { useState } from 'react'
import { tripApi, bookingApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'

export default function TripDetail() {
  const { tripId } = useParams<{ tripId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [seatCount, setSeatCount] = useState(1)
  const [error, setError] = useState('')

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
      navigate(`/customer/bookings/${booking.id}`)
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
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  if (!trip) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Không tìm thấy chuyến xe</p>
        <button onClick={() => navigate('/customer/trips')} className="mt-4 text-primary-600 hover:text-primary-700">
          Quay lại
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/customer/trips')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft size={20} />
        Quay lại
      </button>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-6 text-white">
          <div className="flex items-center gap-3 mb-4">
            <Bus size={32} />
            <div>
              <h1 className="text-2xl font-bold">{trip.route}</h1>
              <p className="text-primary-100">{trip.origin} → {trip.destination}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-sm text-primary-100">Giờ khởi hành</p>
              <p className="text-xl font-bold">{trip.departure_time}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-sm text-primary-100">Giờ đến</p>
              <p className="text-xl font-bold">{trip.arrival_time}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-sm text-primary-100">Giá vé</p>
              <p className="text-xl font-bold">{formatCurrency(trip.price)}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-sm text-primary-100">Ghế trống</p>
              <p className="text-xl font-bold">{trip.available_seats}/{trip.total_seats}</p>
            </div>
          </div>
        </div>

        {/* Booking Form */}
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Đặt vé</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mb-4">
              {error}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="inline mr-2" size={16} />
                Số ghế muốn đặt
              </label>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setSeatCount(Math.max(1, seatCount - 1))}
                  className="w-10 h-10 bg-gray-100 rounded-lg font-bold hover:bg-gray-200"
                >
                  -
                </button>
                <input
                  type="number"
                  min="1"
                  max={trip.available_seats}
                  value={seatCount}
                  onChange={(e) => setSeatCount(Math.max(1, Math.min(trip.available_seats, parseInt(e.target.value) || 1)))}
                  className="w-20 text-center px-4 py-2 border border-gray-300 rounded-lg font-semibold"
                />
                <button
                  onClick={() => setSeatCount(Math.min(trip.available_seats, seatCount + 1))}
                  className="w-10 h-10 bg-gray-100 rounded-lg font-bold hover:bg-gray-200"
                >
                  +
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-2">Tối đa {trip.available_seats} ghế</p>
            </div>

            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Tổng cộng</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Giá mỗi ghế</span>
                  <span>{formatCurrency(trip.price)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Số ghế</span>
                  <span>{seatCount}</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Tổng</span>
                  <span className="text-primary-600">{formatCurrency(trip.price * seatCount)}</span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleBooking}
            disabled={createBookingMutation.isPending || trip.available_seats === 0}
            className="w-full mt-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {createBookingMutation.isPending ? 'Đang xử lý...' : 'Đặt vé ngay'}
          </button>
        </div>
      </div>
    </div>
  )
}
