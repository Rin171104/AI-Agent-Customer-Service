import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Bus, Plus, Pencil, Trash2, MapPin, AlertCircle, Sparkles } from 'lucide-react'
import { tripApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'
import type { CreateTripRequest } from '../../types'
import AIChat from '../../components/AIChat'

export default function OwnerTrips() {
  const queryClient = useQueryClient()
  const [chatOpen, setChatOpen] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editingTrip, setEditingTrip] = useState<string | null>(null)
  const [formData, setFormData] = useState<CreateTripRequest>({
    route: '',
    origin: '',
    destination: '',
    departure_time: '',
    arrival_time: '',
    price: 0,
    total_seats: 0,
  })
  const [error, setError] = useState('')

  const { data: trips, isLoading } = useQuery({
    queryKey: ['trips'],
    queryFn: () => tripApi.getAll().then((res) => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateTripRequest) => tripApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trips'] })
      resetForm()
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Tạo chuyến thất bại')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTripRequest> }) =>
      tripApi.update(id, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trips'] })
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => tripApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trips'] })
    },
  })

  const resetForm = () => {
    setShowForm(false)
    setEditingTrip(null)
    setFormData({
      route: '',
      origin: '',
      destination: '',
      departure_time: '',
      arrival_time: '',
      price: 0,
      total_seats: 0,
    })
    setError('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (editingTrip) {
      updateMutation.mutate({ id: editingTrip, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleEdit = (trip: typeof trips extends (infer T)[] | undefined ? T : never) => {
    setEditingTrip(trip.id)
    setFormData({
      route: trip.route,
      origin: trip.origin,
      destination: trip.destination,
      departure_time: trip.departure_time,
      arrival_time: trip.arrival_time,
      price: trip.price,
      total_seats: trip.total_seats,
    })
    setShowForm(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Bạn có chắc muốn xóa chuyến xe này?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Quản lý chuyến xe</h1>
          <p className="text-neutral-500 mt-1">Thêm, sửa, xóa chuyến xe của bạn</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setChatOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-xl hover:bg-primary-100 transition-colors"
          >
            <Sparkles size={18} className="text-primary-600" />
            <span className="font-medium text-primary-700">Hỏi AI</span>
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="btn-primary"
          >
            <Plus size={18} />
            Thêm chuyến
          </button>
        </div>
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-lg font-bold text-neutral-900 mb-6">
            {editingTrip ? 'Sửa chuyến xe' : 'Thêm chuyến xe mới'}
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center gap-2 mb-4">
              <AlertCircle size={18} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid md:grid-cols-2 gap-5">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Tên tuyến</label>
                <input
                  type="text"
                  value={formData.route}
                  onChange={(e) => setFormData({ ...formData, route: e.target.value })}
                  className="input"
                  placeholder="VD: Hà Nội - Tà Xùa"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Điểm đi</label>
                <input
                  type="text"
                  value={formData.origin}
                  onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
                  className="input"
                  placeholder="VD: Hà Nội"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Điểm đến</label>
                <input
                  type="text"
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  className="input"
                  placeholder="VD: Tà Xùa"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Giờ khởi hành</label>
                <input
                  type="text"
                  value={formData.departure_time}
                  onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
                  className="input"
                  placeholder="VD: 08:00"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Giờ đến</label>
                <input
                  type="text"
                  value={formData.arrival_time}
                  onChange={(e) => setFormData({ ...formData, arrival_time: e.target.value })}
                  className="input"
                  placeholder="VD: 14:00"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Giá vé (VND)</label>
                <input
                  type="number"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: parseInt(e.target.value) || 0 })}
                  className="input"
                  placeholder="VD: 250000"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Tổng số ghế</label>
                <input
                  type="number"
                  value={formData.total_seats}
                  onChange={(e) => setFormData({ ...formData, total_seats: parseInt(e.target.value) || 0 })}
                  className="input"
                  placeholder="VD: 40"
                  required
                />
              </div>
            </div>

            <div className="flex gap-4 pt-2">
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="btn-primary"
              >
                {(createMutation.isPending || updateMutation.isPending) ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Đang xử lý...
                  </span>
                ) : editingTrip ? 'Cập nhật' : 'Tạo mới'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="btn-secondary"
              >
                Hủy
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-card animate-pulse">
              <div className="h-16 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && trips?.length === 0 && (
        <div className="card">
          <div className="empty-state py-16">
            <div className="empty-state-icon">
              <Bus size={32} />
            </div>
            <p className="empty-state-title">Chưa có chuyến xe nào</p>
            <p className="empty-state-description">Thêm chuyến xe mới để bắt đầu</p>
            <button onClick={() => setShowForm(true)} className="btn-primary mt-4">
              Thêm chuyến xe
            </button>
          </div>
        </div>
      )}

      {/* Trips list */}
      {!isLoading && trips && trips.length > 0 && (
        <div className="space-y-4">
          {trips.map((trip) => (
            <div key={trip.id} className="bg-white rounded-2xl p-5 shadow-card">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    trip.status === 'ACTIVE' ? 'bg-primary-50' : 'bg-neutral-100'
                  }`}>
                    <Bus className={trip.status === 'ACTIVE' ? 'text-primary-600' : 'text-neutral-400'} size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-lg text-neutral-900">{trip.route}</span>
                      <span className={`badge ${trip.status === 'ACTIVE' ? 'badge-success' : 'badge-neutral'}`}>
                        {trip.status === 'ACTIVE' ? 'Hoạt động' : 'Đã hủy'}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 mt-2 text-sm text-neutral-500">
                      <span className="flex items-center gap-1">
                        <MapPin size={14} />
                        {trip.origin} → {trip.destination}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      <div className="bg-neutral-50 rounded-lg p-3">
                        <p className="text-xs text-neutral-500">Giờ khởi hành</p>
                        <p className="font-semibold text-neutral-900">{trip.departure_time}</p>
                      </div>
                      <div className="bg-neutral-50 rounded-lg p-3">
                        <p className="text-xs text-neutral-500">Giờ đến</p>
                        <p className="font-semibold text-neutral-900">{trip.arrival_time}</p>
                      </div>
                      <div className="bg-neutral-50 rounded-lg p-3">
                        <p className="text-xs text-neutral-500">Giá vé</p>
                        <p className="font-semibold text-primary-600">{formatCurrency(trip.price)}</p>
                      </div>
                      <div className="bg-neutral-50 rounded-lg p-3">
                        <p className="text-xs text-neutral-500">Ghế trống</p>
                        <p className="font-semibold text-neutral-900">{trip.available_seats}/{trip.total_seats}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(trip)}
                    className="p-2 text-neutral-500 hover:bg-neutral-100 rounded-lg transition-colors"
                  >
                    <Pencil size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(trip.id)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
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
