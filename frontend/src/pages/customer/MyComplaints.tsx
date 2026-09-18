import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MessageSquare, Plus, AlertCircle } from 'lucide-react'
import { complaintApi, bookingApi } from '../../services/api'
import { formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import type { CreateComplaintRequest } from '../../types'

const complaintTypes = [
  { value: 'WRONG_SEAT', label: 'Ghế không đúng' },
  { value: 'LATE', label: 'Xe trễ giờ' },
  { value: 'DRIVER', label: 'Vấn đề tài xế' },
  { value: 'LOST_ITEM', label: 'Mất đồ' },
  { value: 'PAYMENT', label: 'Vấn đề thanh toán' },
  { value: 'BOOKING_ERROR', label: 'Lỗi đặt vé' },
  { value: 'OTHER', label: 'Khác' },
]

const priorities = [
  { value: 'LOW', label: 'Thấp' },
  { value: 'MEDIUM', label: 'Trung bình' },
  { value: 'HIGH', label: 'Cao' },
]

export default function MyComplaints() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CreateComplaintRequest>({
    booking_id: undefined,
    type: 'OTHER',
    description: '',
    priority: 'MEDIUM',
  })
  const [error, setError] = useState('')

  const { data: complaints, isLoading } = useQuery({
    queryKey: ['my-complaints'],
    queryFn: () => complaintApi.getMyComplaints().then((res) => res.data),
  })

  const { data: bookings } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => bookingApi.getMyBookings().then((res) => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateComplaintRequest) =>
      complaintApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-complaints'] })
      setShowForm(false)
      setFormData({ booking_id: undefined, type: 'OTHER', description: '', priority: 'MEDIUM' })
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Tạo khiếu nại thất bại')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!formData.description.trim()) {
      setError('Vui lòng nhập mô tả')
      return
    }
    createMutation.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Khiếu nại</h1>
          <p className="text-gray-500 mt-1">Quản lý các khiếu nại của bạn</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus size={18} />
          Tạo khiếu nại
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Tạo khiếu nại mới</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mb-4 flex items-center gap-2">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Booking (tùy chọn)
                </label>
                <select
                  value={formData.booking_id || ''}
                  onChange={(e) => setFormData({ ...formData, booking_id: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">-- Chọn booking --</option>
                  {bookings?.map((booking) => (
                    <option key={booking.id} value={booking.id}>
                      {booking.booking_code} - {booking.seat_count} ghế
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loại khiếu nại
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {complaintTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mức độ ưu tiên
              </label>
              <div className="flex gap-4">
                {priorities.map((p) => (
                  <label key={p.value} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="priority"
                      value={p.value}
                      checked={formData.priority === p.value}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                      className="w-4 h-4"
                    />
                    {p.label}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mô tả chi tiết <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Mô tả chi tiết vấn đề của bạn..."
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Đang gửi...' : 'Gửi khiếu nại'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50"
              >
                Hủy
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Complaints List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : complaints?.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <MessageSquare className="mx-auto mb-4 text-gray-300" size={64} />
          <p className="text-lg">Chưa có khiếu nại nào</p>
          <p className="text-sm mt-2">Nếu bạn gặp vấn đề, hãy tạo khiếu nại mới</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {complaints?.map((complaint) => (
            <div key={complaint.id} className="bg-white rounded-xl p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-gray-900">{complaint.complaint_code}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(complaint.status)}`}>
                      {getStatusText(complaint.status)}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      complaint.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                      complaint.priority === 'MEDIUM' ? 'bg-orange-100 text-orange-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {complaint.priority === 'HIGH' ? 'Cao' : complaint.priority === 'MEDIUM' ? 'Trung bình' : 'Thấp'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    {complaintTypes.find((t) => t.value === complaint.type)?.label}
                  </p>
                  <p className="text-gray-700 mt-1">{complaint.description}</p>
                  {complaint.owner_note && (
                    <div className="mt-3 bg-gray-50 rounded-lg p-3">
                      <p className="text-sm text-gray-500">Phản hồi từ nhà xe:</p>
                      <p className="text-gray-700">{complaint.owner_note}</p>
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-3">{formatDateTime(complaint.created_at)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
