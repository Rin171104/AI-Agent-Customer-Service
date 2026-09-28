import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Bus, ArrowRight, Clock, MapPin, Ticket, Sparkles } from 'lucide-react'
import { tripApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'
import AIChat from '../../components/AIChat'

export default function SearchTrips() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [chatOpen, setChatOpen] = useState(false)

  const { data: trips, isLoading } = useQuery({
    queryKey: ['trips', origin, destination],
    queryFn: () =>
      tripApi
        .getAll({
          origin: origin || undefined,
          destination: destination || undefined,
        })
        .then((res) => res.data),
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Tìm chuyến xe</h1>
          <p className="text-neutral-500 mt-1">Tìm kiếm chuyến xe phù hợp với lịch trình của bạn</p>
        </div>
        <button
          onClick={() => setChatOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-50 to-accent-50 border border-primary-200 rounded-xl hover:from-primary-100 hover:to-accent-100 transition-colors"
        >
          <Sparkles size={18} className="text-primary-600" />
          <span className="font-medium text-primary-700">Hỏi AI</span>
        </button>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-2xl p-6 shadow-card">
        <form className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-neutral-700 mb-2">Điểm đi</label>
            <div className="relative">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400">
                <MapPin size={18} />
              </div>
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="Nhập điểm đi"
                className="input pl-11"
              />
            </div>
          </div>

          <div className="flex items-center justify-center lg:flex-col lg:justify-center">
            <div className="w-10 h-10 rounded-full bg-primary-50 flex items-center justify-center lg:rotate-90">
              <ArrowRight className="text-primary-600" size={20} />
            </div>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-neutral-700 mb-2">Điểm đến</label>
            <div className="relative">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400">
                <MapPin size={18} />
              </div>
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Nhập điểm đến"
                className="input pl-11"
              />
            </div>
          </div>
        </form>

        {/* Results count */}
        {!isLoading && (
          <div className="mt-4 pt-4 border-t border-neutral-100">
            <p className="text-sm text-neutral-500">
              {trips?.length || 0} chuyến xe được tìm thấy
            </p>
          </div>
        )}
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl p-6 shadow-card animate-pulse">
              <div className="h-20 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && trips?.length === 0 && (
        <div className="bg-white rounded-2xl p-12 shadow-card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <Bus size={32} />
            </div>
            <p className="empty-state-title">Không tìm thấy chuyến xe</p>
            <p className="empty-state-description">Thử thay đổi điểm đi hoặc điểm đến</p>
          </div>
        </div>
      )}

      {/* Trip cards */}
      {!isLoading && trips && trips.length > 0 && (
        <div className="space-y-4">
          {trips.map((trip) => (
            <Link
              key={trip.id}
              to={`/customer/trips/${trip.id}`}
              className="block bg-white rounded-2xl p-5 shadow-card hover:shadow-elevated transition-all duration-200 group"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* Route info */}
                <div className="flex-1">
                  <div className="flex items-center gap-4">
                    <div className="text-center min-w-[80px]">
                      <p className="text-xl font-bold text-neutral-900">{trip.departure_time}</p>
                      <p className="text-sm text-neutral-500">{trip.origin}</p>
                    </div>

                    <div className="flex-1 flex items-center gap-2">
                      <div className="h-px bg-neutral-200 flex-1" />
                      <div className="px-3 py-1 bg-primary-50 rounded-full">
                        <Bus className="text-primary-600" size={16} />
                      </div>
                      <div className="h-px bg-neutral-200 flex-1" />
                    </div>

                    <div className="text-center min-w-[80px]">
                      <p className="text-xl font-bold text-neutral-900">{trip.arrival_time}</p>
                      <p className="text-sm text-neutral-500">{trip.destination}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 mt-4 text-sm text-neutral-500">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      {trip.route}
                    </span>
                    <span className="flex items-center gap-1">
                      <Ticket size={14} />
                      Còn {trip.available_seats}/{trip.total_seats} ghế
                    </span>
                  </div>
                </div>

                {/* Price and action */}
                <div className="flex items-center gap-4 lg:flex-col lg:items-end">
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary-600">{formatCurrency(trip.price)}</p>
                    <p className="text-sm text-neutral-500">/ ghế</p>
                  </div>
                  <button
                    disabled={trip.available_seats === 0}
                    className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed group-hover:scale-105 transition-transform"
                  >
                    {trip.available_seats === 0 ? 'Hết ghế' : 'Đặt vé'}
                  </button>
                </div>
              </div>
            </Link>
          ))}
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
