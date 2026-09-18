import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCcw, Check, X, AlertCircle } from 'lucide-react'
import { refundApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'

export default function OwnerApprovals() {
  const queryClient = useQueryClient()
  const [rejectNote, setRejectNote] = useState('')
  const [showRejectModal, setShowRejectModal] = useState<string | null>(null)

  const { data: refunds, isLoading } = useQuery({
    queryKey: ['pending-refunds'],
    queryFn: () => refundApi.getPendingRefunds().then((res) => res.data),
  })

  const { data: allRefunds } = useQuery({
    queryKey: ['all-refunds'],
    queryFn: () => refundApi.getAllRefunds().then((res) => res.data),
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => refundApi.approve(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-refunds'] })
      queryClient.invalidateQueries({ queryKey: ['all-refunds'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, note }: { id: string; note: string }) =>
      refundApi.reject(id, note).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-refunds'] })
      queryClient.invalidateQueries({ queryKey: ['all-refunds'] })
      setShowRejectModal(null)
    },
  })

  const markRefundedMutation = useMutation({
    mutationFn: (id: string) => refundApi.markRefunded(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-refunds'] })
      queryClient.invalidateQueries({ queryKey: ['all-refunds'] })
    },
  })

  const displayRefunds = allRefunds || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trung tâm phê duyệt</h1>
        <p className="text-gray-500 mt-1">Duyệt và xử lý yêu cầu hoàn tiền</p>
      </div>

      {/* Pending Approvals */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
        <div className="flex items-center gap-2">
          <AlertCircle className="text-yellow-600" size={20} />
          <span className="font-medium text-yellow-800">
            {refunds?.length || 0} yêu cầu đang chờ phê duyệt
          </span>
        </div>
      </div>

      {/* Refunds List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : displayRefunds.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <RefreshCcw className="mx-auto mb-3 text-gray-300" size={64} />
          <p className="text-lg">Không có yêu cầu hoàn tiền nào</p>
        </div>
      ) : (
        <div className="space-y-4">
          {displayRefunds.map((refund) => (
            <div key={refund.id} className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="font-bold text-lg text-gray-900">{refund.refund_code}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(refund.status)}`}>
                      {getStatusText(refund.status)}
                    </span>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <p className="text-sm text-gray-500">Số tiền hoàn</p>
                      <p className="text-xl font-bold text-primary-600">{formatCurrency(refund.amount)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Ngân hàng</p>
                      <p className="font-medium">{refund.bank_name}</p>
                      <p className="text-sm text-gray-600">{refund.account_number}</p>
                      <p className="text-sm text-gray-600">{refund.account_holder}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Ngày tạo</p>
                      <p className="font-medium">{formatDateTime(refund.created_at)}</p>
                    </div>
                  </div>

                  {refund.reason && (
                    <div className="mt-4 bg-gray-50 rounded-lg p-3">
                      <p className="text-sm text-gray-500">Lý do:</p>
                      <p className="text-gray-700">{refund.reason}</p>
                    </div>
                  )}

                  {refund.complaint && (
                    <div className="mt-4 bg-orange-50 rounded-lg p-3">
                      <p className="text-sm text-orange-600">Khiếu nại liên quan:</p>
                      <p className="font-medium">{refund.complaint.complaint_code}</p>
                      <p className="text-sm text-gray-600">{refund.complaint.description}</p>
                    </div>
                  )}

                  {refund.owner_note && (
                    <div className="mt-4 bg-blue-50 rounded-lg p-3">
                      <p className="text-sm text-blue-600">Ghi chú:</p>
                      <p className="text-gray-700">{refund.owner_note}</p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2">
                  {refund.status === 'WAITING_OWNER_APPROVAL' && (
                    <>
                      <button
                        onClick={() => approveMutation.mutate(refund.id)}
                        disabled={approveMutation.isPending}
                        className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                      >
                        <Check size={18} />
                        Phê duyệt
                      </button>
                      <button
                        onClick={() => setShowRejectModal(refund.id)}
                        className="flex items-center gap-2 px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700"
                      >
                        <X size={18} />
                        Từ chối
                      </button>
                    </>
                  )}
                  {refund.status === 'APPROVED' && (
                    <button
                      onClick={() => markRefundedMutation.mutate(refund.id)}
                      disabled={markRefundedMutation.isPending}
                      className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50"
                    >
                      <RefreshCcw size={18} />
                      {markRefundedMutation.isPending ? 'Đang xử lý...' : 'Đánh dấu đã hoàn tiền'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="font-semibold text-lg text-gray-900 mb-4">Từ chối yêu cầu hoàn tiền</h3>
            <textarea
              value={rejectNote}
              onChange={(e) => setRejectNote(e.target.value)}
              placeholder="Nhập lý do từ chối..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
              rows={4}
            />
            <div className="flex gap-4">
              <button
                onClick={() => {
                  if (rejectNote) {
                    rejectMutation.mutate({ id: showRejectModal, note: rejectNote })
                  }
                }}
                disabled={!rejectNote || rejectMutation.isPending}
                className="flex-1 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50"
              >
                {rejectMutation.isPending ? 'Đang xử lý...' : 'Xác nhận từ chối'}
              </button>
              <button
                onClick={() => {
                  setShowRejectModal(null)
                  setRejectNote('')
                }}
                className="px-6 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50"
              >
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
