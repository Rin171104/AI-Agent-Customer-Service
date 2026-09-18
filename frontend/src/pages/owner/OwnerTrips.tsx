import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bus, Plus, Edit, Trash2, AlertCircle } from 'lucide-react'
import { tripApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'
import type { CreateTripRequest } from '../../types'

export default function OwnerTrips() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingTrip, setEditingTrip] = useState<string | null>(null)
  const [formData, setFormData] = useState<CreateTripRequest>({
    route: '',
    origin: '',
    destination: '',
    departure_time: '',
    arrival_time: '',
    price: 0,
    total_seats: 40,
  })
  const [error, setError] = useState('')

  const { data: trips, isLoading } = useQuery({
    queryKey: ['all-trips'],
    queryFn: () => tripApi.getAll().then((res) => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateTripRequest) => tripApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-trips'] })
      resetForm()
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Tạo thất bại')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTripRequest> }) =>
      tripApi.update(id, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-trips'] })
      resetForm()
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Cập nhật thất bại')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => tripApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-trips'] })
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
      total_seats: 40,
    })
    setError('')
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.route || !formData.origin || !formData.destination || !formData.departure_time || !formData.arrival_time) {
      setError('Vui lòng điền đầy đủ thông tin')
      return
    }

    if (editingTrip) {
      updateMutation.mutate({ id: editingTrip, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: string, route: string) => {
    if (confirm(`Bạn có chắc muốn xóa chuyến ${route}?`)) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quản lý chuyến xe</h1>
          <p className="text-gray-500 mt-1">Thêm, sửa, xóa các chuyến xe</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus size={18} />
          Thêm chuyến
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">
            {editingTrip ? 'Sửa chuyến xe' : 'Thêm chuyến xe mới'}
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mb-4 flex items-center gap-2">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tuyến</label>
              <input
                type="text"
                value={formData.route}
                onChange={(e) => setFormData({ ...formData, route: e.target.value })}
                placeholder="VD: HN-TXS"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Điểm đi</label>
              <input
                type="text"
                value={formData.origin}
                onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
                placeholder="VD: Hà Nội"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Điểm đến</label>
              <input
                type="text"
                value={formData.destination}
                onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                placeholder="VD: Tà Xùa"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Giờ khởi hành</label>
              <input
                type="text"
                value={formData.departure_time}
                onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
                placeholder="VD: 06:00"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Giờ đến</label>
              <input
                type="text"
                value={formData.arrival_time}
                onChange={(e) => setFormData({ ...formData, arrival_time: e.target.value })}
                placeholder="VD: 10:00"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Giá (VND)</label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseInt(e.target.value) || 0 })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tổng số ghế</label>
              <input
                type="number"
                value={formData.total_seats}
                onChange={(e) => setFormData({ ...formData, total_seats: parseInt(e.target.value) || 40 })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="md:col-span-3 flex gap-4 mt-4">
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
              >
                {createMutation.isPending || updateMutation.isPending ? 'Đang xử lý...' : editingTrip ? 'Cập nhật' : 'Tạo mới'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50"
              >
                Hủy
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Trips List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tuyến</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lộ trình</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giờ</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giá</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ghế</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Hành động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {trips?.map((trip) => (
                <tr key={trip.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{trip.route}</td>
                  <td className="px-6 py-4 text-gray-600">{trip.origin} → {trip.destination}</td>
                  <td className="px-6 py-4 text-gray-600">{trip.departure_time} - {trip.arrival_time}</td>
                  <td className="px-6 py-4 text-gray-600">{formatCurrency(trip.price)}</td>
                  <td className="px-6 py-4 text-gray-600">{trip.available_seats}/{trip.total_seats}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      trip.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {trip.status === 'ACTIVE' ? 'Hoạt động' : 'Đã hủy'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleEdit(trip)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      <Edit size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(trip.id, trip.route)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg ml-2"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {trips?.length === 0 && (
            <div className="p-12 text-center text-gray-500">
              <Bus className="mx-auto mb-3 text-gray-300" size={48} />
              <p>Chưa có chuyến xe nào</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
