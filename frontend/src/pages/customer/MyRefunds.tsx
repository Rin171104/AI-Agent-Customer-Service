import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCcw, Plus, AlertCircle, Check, Clock, Sparkles, Banknote, FileText } from 'lucide-react'
import { refundApi, bookingApi, complaintApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import type { CreateRefundRequest } from '../../types'
import AIChat from '../../components/AIChat'

export default function MyRefunds() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const [formData, setFormData] = useState<CreateRefundRequest>({
    complaint_id: undefined,
    booking_id: '',
    amount: 0,
    bank_name: '',
    account_number: '',
    account_holder: '',
    reason: '',
  })
  const [error, setError] = useState('')

  const { data: refunds, isLoading } = useQuery({
    queryKey: ['my-refunds'],
    queryFn: () => refundApi.getMyRefunds().then((res) => res.data),
  })

  const { data: bookings } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => bookingApi.getMyBookings().then((res) => res.data),
  })

  const { data: complaints } = useQuery({
    queryKey: ['my-complaints'],
    queryFn: () => complaintApi.getMyComplaints().then((res) => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateRefundRequest) =>
      refundApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-refunds'] })
      setShowForm(false)
      setFormData({
        complaint_id: undefined,
        booking_id: '',
        amount: 0,
        bank_name: '',
        account_number: '',
        account_holder: '',
        reason: '',
      })
      setError('')
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Tạo yêu cầu thất bại')
    },
  })

  const handleBookingChange = (bookingId: string) => {
    const booking = bookings?.find((b) => b.id === bookingId)
    setFormData({
      ...formData,
      booking_id: bookingId,
      amount: booking?.total_amount || 0,
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!formData.booking_id) {
      setError('Vui lòng chọn booking')
      return
    }
    if (!formData.bank_name || !formData.account_number || !formData.account_holder) {
      setError('Vui lòng điền đầy đủ thông tin tài khoản')
      return
    }
    createMutation.mutate(formData)
  }

  const getStatusSteps = (status: string) => {
    const steps = [
      { key: 'REQUESTED', label: 'Đã gửi', icon: Clock },
      { key: 'WAITING_OWNER_APPROVAL', label: 'Chờ duyệt', icon: Clock },
      { key: 'APPROVED', label: 'Đã duyệt', icon: Check },
      { key: 'REFUNDED', label: 'Đã hoàn tiền', icon: Check },
    ]

    const statusOrder = ['REQUESTED', 'WAITING_OWNER_APPROVAL', 'APPROVED', 'REFUNDED', 'REJECTED']
    const currentIndex = statusOrder.indexOf(status)
    const isRejected = status === 'REJECTED'

    return { steps, currentIndex, isRejected }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Yêu cầu hoàn tiền</h1>
          <p className="text-neutral-500 mt-1">Theo dõi và tạo yêu cầu hoàn tiền</p>
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
            Tạo yêu cầu
          </button>
        </div>
      </div>

      {/* Info banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
        <AlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
        <div>
          <p className="font-medium text-blue-900">Lưu ý về quy trình hoàn tiền</p>
          <p className="text-sm text-blue-700 mt-1">
            Yêu cầu hoàn tiền sẽ được gửi đến chủ nhà xe để xét duyệt. Sau khi được duyệt, chủ nhà xe sẽ chuyển tiền thủ công vào tài khoản của bạn.
          </p>
        </div>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-lg font-bold text-neutral-900 mb-6">Tạo yêu cầu hoàn tiền mới</h2>

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
                  Booking liên quan <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.booking_id}
                  onChange={(e) => handleBookingChange(e.target.value)}
                  className="input"
                >
                  <option value="">-- Chọn booking --</option>
                  {bookings?.map((booking) => (
                    <option key={booking.id} value={booking.id}>
                      {booking.booking_code} - {formatCurrency(booking.total_amount)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Khiếu nại (tùy chọn)
                </label>
                <select
                  value={formData.complaint_id || ''}
                  onChange={(e) => setFormData({ ...formData, complaint_id: e.target.value || undefined })}
                  className="input"
                >
                  <option value="">-- Chọn khiếu nại --</option>
                  {complaints?.map((complaint) => (
                    <option key={complaint.id} value={complaint.id}>
                      {complaint.complaint_code} - {complaint.type}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Số tiền hoàn <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: parseInt(e.target.value) || 0 })}
                className="input max-w-xs"
                placeholder="0"
              />
            </div>

            <div className="border-t border-neutral-100 pt-5">
              <h3 className="font-medium text-neutral-900 mb-4 flex items-center gap-2">
                <Banknote size={18} className="text-neutral-500" />
                Thông tin tài khoản nhận tiền
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Tên ngân hàng <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.bank_name}
                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                    placeholder="VD: Vietcombank"
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Số tài khoản <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.account_number}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                    placeholder="1234567890"
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Tên chủ tài khoản <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.account_holder}
                    onChange={(e) => setFormData({ ...formData, account_holder: e.target.value })}
                    placeholder="NGUYEN VAN A"
                    className="input"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Lý do (tùy chọn)
              </label>
              <textarea
                value={formData.reason || ''}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                rows={3}
                className="input resize-none"
                placeholder="Mô tả lý do yêu cầu hoàn tiền..."
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
                    Gửi yêu cầu
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
          {[1, 2].map((i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-card animate-pulse">
              <div className="h-24 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && refunds?.length === 0 && (
        <div className="card">
          <div className="empty-state py-16">
            <div className="empty-state-icon">
              <RefreshCcw size={32} />
            </div>
            <p className="empty-state-title">Chưa có yêu cầu hoàn tiền nào</p>
            <p className="empty-state-description">Tạo yêu cầu mới nếu bạn cần hoàn tiền</p>
            <button onClick={() => setShowForm(true)} className="btn-primary mt-4">
              Tạo yêu cầu
            </button>
          </div>
        </div>
      )}

      {/* Refunds list */}
      {!isLoading && refunds && refunds.length > 0 && (
        <div className="space-y-4">
          {refunds.map((refund) => {
            const { steps, currentIndex, isRejected } = getStatusSteps(refund.status)
            return (
              <div key={refund.id} className="bg-white rounded-2xl p-5 shadow-card">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="font-bold text-lg text-neutral-900">{refund.refund_code}</span>
                      <span className={`badge ${getStatusColor(refund.status)}`}>
                        {getStatusText(refund.status)}
                      </span>
                    </div>
                    <p className="text-3xl font-bold text-primary-600 mt-2">{formatCurrency(refund.amount)}</p>

                    <div className="mt-4 space-y-2 text-sm">
                      <p className="text-neutral-600">
                        <span className="text-neutral-400">Ngân hàng:</span> {refund.bank_name}
                      </p>
                      <p className="text-neutral-600">
                        <span className="text-neutral-400">STK:</span> {refund.account_number}
                      </p>
                      <p className="text-neutral-600">
                        <span className="text-neutral-400">Chủ TK:</span> {refund.account_holder}
                      </p>
                    </div>

                    {refund.reason && (
                      <div className="mt-4 bg-neutral-50 rounded-xl p-3">
                        <p className="text-sm text-neutral-500">Lý do:</p>
                        <p className="text-neutral-700">{refund.reason}</p>
                      </div>
                    )}

                    {refund.owner_note && (
                      <div className="mt-4 bg-blue-50 rounded-xl p-3 border border-blue-100">
                        <p className="text-sm text-blue-600 font-medium">Ghi chú từ nhà xe:</p>
                        <p className="text-neutral-700 mt-1">{refund.owner_note}</p>
                      </div>
                    )}

                    {refund.status === 'WAITING_OWNER_APPROVAL' && (
                      <div className="mt-4 bg-amber-50 border border-amber-200 rounded-xl p-4">
                        <div className="flex items-center gap-2 text-amber-800 font-medium mb-1">
                          <Clock size={18} />
                          Đang chờ xác nhận
                        </div>
                        <p className="text-sm text-amber-700">
                          Yêu cầu của bạn đang chờ chủ nhà xe xác nhận. Vui lòng đợi trong giây lát.
                        </p>
                      </div>
                    )}

                    <p className="text-xs text-neutral-400 mt-4">{formatDateTime(refund.created_at)}</p>
                  </div>
                </div>

                {/* Progress Steps */}
                <div className="mt-6 pt-6 border-t border-neutral-100">
                  <div className="flex items-center justify-between">
                    {steps.map((step, index) => {
                      const Icon = step.icon
                      const isActive = isRejected
                        ? step.key === 'REQUESTED'
                        : index <= currentIndex
                      const isCurrent = isRejected
                        ? step.key === 'REJECTED'
                        : index === currentIndex

                      return (
                        <div key={step.key} className="flex items-center">
                          <div className="flex flex-col items-center">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              step.key === 'REJECTED'
                                ? 'bg-red-100 text-red-600'
                                : isActive
                                ? 'bg-green-100 text-green-600'
                                : 'bg-neutral-100 text-neutral-400'
                            }`}>
                              {step.key === 'REJECTED' ? (
                                <span className="font-bold">✕</span>
                              ) : (
                                <Icon size={18} />
                              )}
                            </div>
                            <span className={`text-xs mt-2 text-center ${
                              isCurrent ? 'font-medium text-neutral-900' : 'text-neutral-400'
                            }`}>
                              {step.label}
                            </span>
                          </div>
                          {index < steps.length - 1 && (
                            <div className={`w-12 lg:w-20 h-0.5 mx-1 lg:mx-2 ${
                              isRejected && index === 0
                                ? 'bg-neutral-200'
                                : !isRejected && index < currentIndex
                                ? 'bg-green-300'
                                : 'bg-neutral-200'
                            }`} />
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )
          })}
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
