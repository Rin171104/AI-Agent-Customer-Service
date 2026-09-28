import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MessageSquare, Plus, AlertCircle, Check, Clock, Sparkles, FileText } from 'lucide-react'
import { complaintApi, bookingApi } from '../../services/api'
import { formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import type { CreateComplaintRequest } from '../../types'
import AIChat from '../../components/AIChat'

const complaintTypes = [
  { value: 'WRONG_SEAT', label: 'Ghế không đúng' },
  { value: 'LATE', label: 'Xe trễ giờ' },
  { value: 'DRIVER', label: 'Vấn đề tài xế' },
  { value: 'LOST_ITEM', label: 'Mất đồ' },
  { value: 'PAYMENT', label: 'Vấn đề thanh toán' },
  { value: 'BOOKING_ERROR', label: 'Lỗi đặt vé' },
  { value: 'REFUND', label: 'Yêu cầu hoàn tiền' },
  { value: 'OTHER', label: 'Khác' },
]

const priorities = [
  { value: 'LOW', label: 'Thấp', color: 'bg-neutral-100 text-neutral-700' },
  { value: 'MEDIUM', label: 'Trung bình', color: 'bg-amber-100 text-amber-700' },
  { value: 'HIGH', label: 'Cao', color: 'bg-red-100 text-red-700' },
]

export default function MyComplaints() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
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
      setError('')
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'OPEN':
        return <Clock className="text-blue-600" size={16} />
      case 'IN_PROGRESS':
        return <AlertCircle className="text-amber-600" size={16} />
      case 'RESOLVED':
        return <Check className="text-green-600" size={16} />
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Khiếu nại</h1>
          <p className="text-neutral-500 mt-1">Theo dõi và tạo khiếu nại mới</p>
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
            onClick={() => setShowForm(!showForm)}
            className="btn-primary"
          >
            <Plus size={18} />
            Tạo khiếu nại
          </button>
        </div>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-lg font-bold text-neutral-900 mb-6">Tạo khiếu nại mới</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center gap-2 mb-4">
              <AlertCircle size={18} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid md:grid-cols-2 gap-5">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Booking liên quan (tùy chọn)
                </label>
                <select
                  value={formData.booking_id || ''}
                  onChange={(e) => setFormData({ ...formData, booking_id: e.target.value || undefined })}
                  className="input"
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
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Loại khiếu nại
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="input"
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
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Mức độ ưu tiên
              </label>
              <div className="flex gap-3">
                {priorities.map((p) => (
                  <label
                    key={p.value}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors ${
                      formData.priority === p.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-neutral-200 hover:bg-neutral-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="priority"
                      value={p.value}
                      checked={formData.priority === p.value}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                      className="sr-only"
                    />
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${p.color}`}>
                      {p.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Mô tả chi tiết <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="input resize-none"
                placeholder="Mô tả chi tiết vấn đề của bạn..."
              />
            </div>

            <div className="flex gap-4 pt-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="btn-primary"
              >
                {createMutation.isPending ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Đang gửi...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <FileText size={18} />
                    Gửi khiếu nại
                  </span>
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setError('')
                }}
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
              <div className="h-20 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && complaints?.length === 0 && (
        <div className="card">
          <div className="empty-state py-16">
            <div className="empty-state-icon">
              <MessageSquare size={32} />
            </div>
            <p className="empty-state-title">Chưa có khiếu nại nào</p>
            <p className="empty-state-description">Nếu bạn gặp vấn đề, hãy tạo khiếu nại mới</p>
            <button onClick={() => setShowForm(true)} className="btn-primary mt-4">
              Tạo khiếu nại
            </button>
          </div>
        </div>
      )}

      {/* Complaints list */}
      {!isLoading && complaints && complaints.length > 0 && (
        <div className="space-y-4">
          {complaints.map((complaint) => (
            <div key={complaint.id} className="bg-white rounded-2xl p-5 shadow-card">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    complaint.status === 'RESOLVED' ? 'bg-green-50' :
                    complaint.status === 'IN_PROGRESS' ? 'bg-amber-50' :
                    'bg-blue-50'
                  }`}>
                    {getStatusIcon(complaint.status)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-neutral-900">{complaint.complaint_code}</span>
                      <span className={`badge ${getStatusColor(complaint.status)}`}>
                        {getStatusText(complaint.status)}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        complaint.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                        complaint.priority === 'MEDIUM' ? 'bg-amber-100 text-amber-700' :
                        'bg-neutral-100 text-neutral-700'
                      }`}>
                        {complaint.priority === 'HIGH' ? 'Cao' : complaint.priority === 'MEDIUM' ? 'Trung bình' : 'Thấp'}
                      </span>
                    </div>
                    <p className="text-sm text-neutral-500 mt-1">
                      {complaintTypes.find((t) => t.value === complaint.type)?.label}
                    </p>
                    <p className="text-neutral-700 mt-2">{complaint.description}</p>
                    {complaint.owner_note && (
                      <div className="mt-4 bg-accent-50 rounded-xl p-4 border border-accent-100">
                        <div className="flex items-center gap-2 text-accent-700 font-medium mb-2">
                          <MessageSquare size={16} />
                          Phản hồi từ nhà xe:
                        </div>
                        <p className="text-neutral-700">{complaint.owner_note}</p>
                      </div>
                    )}
                    <p className="text-xs text-neutral-400 mt-3">{formatDateTime(complaint.created_at)}</p>
                  </div>
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
            <AIChat context="customer" embedded onClose={() => setChatOpen(false)} />
          </div>
        </div>
      )}
    </div>
  )
}
