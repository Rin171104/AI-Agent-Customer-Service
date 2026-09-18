import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Bus, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { tripApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'

export default function SearchTrips() {
  const navigate = useNavigate()
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')

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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
  }

  const handleSelectTrip = (tripId: string) => {
    navigate(`/customer/trips/${tripId}`)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tìm chuyến xe</h1>
        <p className="text-gray-500 mt-1">Tìm kiếm chuyến xe phù hợp với lịch trình của bạn</p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="bg-white rounded-xl p-6 shadow-sm">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Điểm đi</label>
            <div className="relative">
              <Bus className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="Ví dụ: Hà Nội"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Điểm đến</label>
            <div className="relative">
              <Bus className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Ví dụ: Tà Xùa"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
              />
            </div>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 flex items-center justify-center gap-2"
            >
              <Search size={20} />
              Tìm kiếm
            </button>
          </div>
        </div>
      </form>

      {/* Results */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {isLoading ? 'Đang tải...' : `${trips?.length || 0} chuyến xe được tìm thấy`}
        </h2>

        {trips?.length === 0 && (
          <div className="bg-white rounded-xl p-8 text-center text-gray-500">
            <Bus className="mx-auto mb-3 text-gray-300" size={48} />
            <p>Không tìm thấy chuyến xe nào</p>
            <p className="text-sm mt-1">Thử thay đổi điểm đi, điểm đến</p>
          </div>
        )}

        <div className="grid gap-4">
          {trips?.map((trip) => (
            <div key={trip.id} className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <p className="text-xl font-bold text-gray-900">{trip.departure_time}</p>
                      <p className="text-sm text-gray-500">{trip.origin}</p>
                    </div>
                    <div className="flex-1 flex items-center">
                      <div className="h-px bg-gray-300 flex-1" />
                      <ArrowRight className="text-gray-400 mx-2" size={20} />
                      <div className="h-px bg-gray-300 flex-1" />
                    </div>
                    <div className="text-center">
                      <p className="text-xl font-bold text-gray-900">{trip.arrival_time}</p>
                      <p className="text-sm text-gray-500">{trip.destination}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                    <span>Tuyến: {trip.route}</span>
                    <span>•</span>
                    <span>Còn {trip.available_seats}/{trip.total_seats} ghế</span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary-600">{formatCurrency(trip.price)}</p>
                    <p className="text-sm text-gray-500">/ ghế</p>
                  </div>
                  <button
                    onClick={() => handleSelectTrip(trip.id)}
                    disabled={trip.available_seats === 0}
                    className="px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Đặt vé
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
