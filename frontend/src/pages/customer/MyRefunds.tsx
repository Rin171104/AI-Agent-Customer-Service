import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCcw, Plus, AlertCircle, Check } from 'lucide-react'
import { refundApi, bookingApi, complaintApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import type { CreateRefundRequest } from '../../types'

export default function MyRefunds() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
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
      { key: 'WAITING_OWNER_APPROVAL', label: 'Chờ duyệt' },
      { key: 'APPROVED', label: 'Đã duyệt' },
      { key: 'REFUNDED', label: 'Đã hoàn tiền' },
    ]

    const rejected = status === 'REJECTED'
    const currentIndex = steps.findIndex((s) => s.key === status)

    return { steps, currentIndex, rejected }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Yêu cầu hoàn tiền</h1>
          <p className="text-gray-500 mt-1">Theo dõi và tạo yêu cầu hoàn tiền</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus size={18} />
          Tạo yêu cầu
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Tạo yêu cầu hoàn tiền mới</h2>

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
                  Booking liên quan
                </label>
                <select
                  value={formData.booking_id}
                  onChange={(e) => handleBookingChange(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Khiếu nại (tùy chọn)
                </label>
                <select
                  value={formData.complaint_id || ''}
                  onChange={(e) => setFormData({ ...formData, complaint_id: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">-- Chọn khiếu nại (nếu có) --</option>
                  {complaints?.map((complaint) => (
                    <option key={complaint.id} value={complaint.id}>
                      {complaint.complaint_code} - {complaint.type}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Số tiền hoàn
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: parseInt(e.target.value) || 0 })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div className="border-t pt-4">
              <h3 className="font-medium text-gray-900 mb-3">Thông tin tài khoản nhận tiền</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tên ngân hàng</label>
                  <input
                    type="text"
                    value={formData.bank_name}
                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                    placeholder="VD: Vietcombank"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Số tài khoản</label>
                  <input
                    type="text"
                    value={formData.account_number}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                    placeholder="1234567890"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tên chủ tài khoản</label>
                  <input
                    type="text"
                    value={formData.account_holder}
                    onChange={(e) => setFormData({ ...formData, account_holder: e.target.value })}
                    placeholder="NGUYEN VAN A"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Lý do (tùy chọn)</label>
              <textarea
                value={formData.reason || ''}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Mô tả lý do yêu cầu hoàn tiền..."
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Đang gửi...' : 'Gửi yêu cầu'}
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

      {/* Refunds List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : refunds?.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <RefreshCcw className="mx-auto mb-4 text-gray-300" size={64} />
          <p className="text-lg">Chưa có yêu cầu hoàn tiền nào</p>
          <p className="text-sm mt-2">Tạo yêu cầu mới nếu bạn cần hoàn tiền</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {refunds?.map((refund) => {
            const { steps, currentIndex, rejected } = getStatusSteps(refund.status)
            return (
              <div key={refund.id} className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-gray-900">{refund.refund_code}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(refund.status)}`}>
                        {getStatusText(refund.status)}
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-primary-600 mt-2">{formatCurrency(refund.amount)}</p>
                    <p className="text-sm text-gray-500 mt-2">
                      {refund.bank_name} - {refund.account_number}
                    </p>
                    {refund.reason && (
                      <p className="text-gray-700 mt-2 text-sm">{refund.reason}</p>
                    )}
                    {refund.owner_note && (
                      <div className="mt-3 bg-gray-50 rounded-lg p-3">
                        <p className="text-sm text-gray-500">Ghi chú từ nhà xe:</p>
                        <p className="text-gray-700">{refund.owner_note}</p>
                      </div>
                    )}
                    <p className="text-xs text-gray-400 mt-3">{formatDateTime(refund.created_at)}</p>
                  </div>
                </div>

                {/* Progress Steps */}
                <div className="mt-4">
                  <div className="flex items-center justify-between">
                    {steps.map((step, index) => (
                      <div key={step.key} className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          rejected && step.key === 'APPROVED' ? 'bg-red-100 text-red-600' :
                          index <= currentIndex && !rejected ? 'bg-green-100 text-green-600' :
                          'bg-gray-100 text-gray-400'
                        }`}>
                          {rejected && step.key === 'APPROVED' ? (
                            <AlertCircle size={16} />
                          ) : index <= currentIndex && !rejected ? (
                            <Check size={16} />
                          ) : (
                            <span className="text-xs">{index + 1}</span>
                          )}
                        </div>
                        <span className={`ml-2 text-sm ${
                          (rejected && step.key === 'APPROVED') || (index <= currentIndex && !rejected)
                            ? 'text-gray-900 font-medium'
                            : 'text-gray-400'
                        }`}>
                          {step.label}
                        </span>
                        {index < steps.length - 1 && (
                          <div className={`w-12 h-0.5 mx-2 ${
                            (rejected && index === 0) || (index < currentIndex && !rejected)
                              ? 'bg-green-300'
                              : 'bg-gray-200'
                          }`} />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
