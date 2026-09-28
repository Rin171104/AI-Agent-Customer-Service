import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { MessageSquare, Clock, AlertCircle, Check, Sparkles, Ticket } from 'lucide-react'
import { complaintApi } from '../../services/api'
import { formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
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

export default function OwnerComplaints() {
  const queryClient = useQueryClient()
  const [chatOpen, setChatOpen] = useState(false)
  const [selectedComplaint, setSelectedComplaint] = useState<string | null>(null)
  const [resolveNote, setResolveNote] = useState('')

  const { data: complaints, isLoading } = useQuery({
    queryKey: ['all-complaints'],
    queryFn: () => complaintApi.getAllComplaints().then((res) => res.data),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { status?: string; owner_note?: string } }) =>
      complaintApi.update(id, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-complaints'] })
      setSelectedComplaint(null)
      setResolveNote('')
    },
  })

  const resolveMutation = useMutation({
    mutationFn: ({ id, note }: { id: string; note: string }) =>
      complaintApi.resolve(id, note).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-complaints'] })
      setSelectedComplaint(null)
      setResolveNote('')
    },
  })

  const handleResolve = (id: string) => {
    if (!resolveNote.trim()) return
    resolveMutation.mutate({ id, note: resolveNote })
  }

  const openComplaints = complaints?.filter((c) => c.status === 'OPEN') || []
  const inProgressComplaints = complaints?.filter((c) => c.status === 'IN_PROGRESS') || []
  const resolvedComplaints = complaints?.filter((c) => c.status === 'RESOLVED') || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Quản lý khiếu nại</h1>
          <p className="text-neutral-500 mt-1">Xem và xử lý khiếu nại từ khách hàng</p>
        </div>
        <button
          onClick={() => setChatOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-xl hover:bg-primary-100 transition-colors"
        >
          <Sparkles size={18} className="text-primary-600" />
          <span className="font-medium text-primary-700">Hỏi AI</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 text-center">
          <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-3">
            <Clock className="text-blue-600" size={24} />
          </div>
          <p className="text-3xl font-bold text-blue-600">{openComplaints.length}</p>
          <p className="text-sm text-blue-700 mt-1">Khiếu nại mới</p>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 text-center">
          <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-3">
            <AlertCircle className="text-amber-600" size={24} />
          </div>
          <p className="text-3xl font-bold text-amber-600">{inProgressComplaints.length}</p>
          <p className="text-sm text-amber-700 mt-1">Đang xử lý</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-center">
          <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
            <Check className="text-green-600" size={24} />
          </div>
          <p className="text-3xl font-bold text-green-600">{resolvedComplaints.length}</p>
          <p className="text-sm text-green-700 mt-1">Đã giải quyết</p>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-card animate-pulse">
              <div className="h-24 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && complaints?.length === 0 && (
        <div className="bg-white rounded-2xl p-12 shadow-card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <MessageSquare size={32} />
            </div>
            <p className="empty-state-title">Không có khiếu nại nào</p>
            <p className="empty-state-description">Mọi thứ đang hoạt động tốt!</p>
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
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    complaint.status === 'RESOLVED' ? 'bg-green-50' :
                    complaint.status === 'IN_PROGRESS' ? 'bg-amber-50' :
                    'bg-blue-50'
                  }`}>
                    {complaint.status === 'RESOLVED' ? (
                      <Check className="text-green-600" size={20} />
                    ) : complaint.status === 'IN_PROGRESS' ? (
                      <AlertCircle className="text-amber-600" size={20} />
                    ) : (
                      <Clock className="text-blue-600" size={20} />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-lg text-neutral-900">{complaint.complaint_code}</span>
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
                      <span className="text-sm text-neutral-500">
                        {complaintTypes.find((t) => t.value === complaint.type)?.label}
                      </span>
                    </div>

                    <p className="text-neutral-700 mt-2">{complaint.description}</p>

                    {complaint.booking && (
                      <div className="mt-3 bg-neutral-50 rounded-lg p-3 flex items-center gap-2">
                        <Ticket size={16} className="text-neutral-400" />
                        <span className="text-sm text-neutral-600">
                          Booking: {complaint.booking.booking_code} - {complaint.booking.seat_count} ghế
                        </span>
                      </div>
                    )}

                    {complaint.owner_note && (
                      <div className="mt-4 bg-accent-50 rounded-xl p-4 border border-accent-100">
                        <p className="text-sm font-medium text-accent-700 mb-1">Phản hồi của bạn:</p>
                        <p className="text-neutral-700">{complaint.owner_note}</p>
                      </div>
                    )}

                    <p className="text-xs text-neutral-400 mt-3">{formatDateTime(complaint.created_at)}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  {complaint.status === 'OPEN' && (
                    <button
                      onClick={() => updateMutation.mutate({ id: complaint.id, data: { status: 'IN_PROGRESS' } })}
                      disabled={updateMutation.isPending}
                      className="btn-primary text-sm"
                    >
                      Tiếp nhận
                    </button>
                  )}
                  {complaint.status === 'IN_PROGRESS' && (
                    <button
                      onClick={() => setSelectedComplaint(complaint.id)}
                      className="btn-success text-sm"
                    >
                      Giải quyết
                    </button>
                  )}
                </div>
              </div>

              {/* Resolve modal */}
              {selectedComplaint === complaint.id && (
                <div className="mt-6 pt-6 border-t border-neutral-100">
                  <h4 className="font-medium text-neutral-900 mb-3">Giải quyết khiếu nại</h4>
                  <textarea
                    value={resolveNote}
                    onChange={(e) => setResolveNote(e.target.value)}
                    placeholder="Nhập ghi chú giải quyết..."
                    rows={3}
                    className="input resize-none"
                  />
                  <div className="flex gap-3 mt-3">
                    <button
                      onClick={() => handleResolve(complaint.id)}
                      disabled={!resolveNote.trim() || resolveMutation.isPending}
                      className="btn-success"
                    >
                      {resolveMutation.isPending ? 'Đang xử lý...' : 'Xác nhận giải quyết'}
                    </button>
                    <button
                      onClick={() => {
                        setSelectedComplaint(null)
                        setResolveNote('')
                      }}
                      className="btn-secondary"
                    >
                      Hủy
                    </button>
                  </div>
                </div>
              )}
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
