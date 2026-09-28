import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCcw, Check, X, AlertCircle, Sparkles, Clock, Banknote, CheckCircle } from 'lucide-react'
import { refundApi } from '../../services/api'
import { formatCurrency, formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'
import AIChat from '../../components/AIChat'

export default function OwnerApprovals() {
  const queryClient = useQueryClient()
  const [chatOpen, setChatOpen] = useState(false)
  const [rejectModal, setRejectModal] = useState<string | null>(null)
  const [rejectNote, setRejectNote] = useState('')

  const { data: refunds, isLoading } = useQuery({
    queryKey: ['all-refunds'],
    queryFn: () => refundApi.getAllRefunds().then((res) => res.data),
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => refundApi.approve(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-refunds'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, note }: { id: string; note: string }) =>
      refundApi.reject(id, note).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-refunds'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      setRejectModal(null)
      setRejectNote('')
    },
  })

  const markRefundedMutation = useMutation({
    mutationFn: (id: string) => refundApi.markRefunded(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-refunds'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
    },
  })

  const pendingRefunds = refunds?.filter((r) => r.status === 'WAITING_OWNER_APPROVAL') || []
  const approvedRefunds = refunds?.filter((r) => r.status === 'APPROVED') || []
  const otherRefunds = refunds?.filter((r) => !['WAITING_OWNER_APPROVAL', 'APPROVED'].includes(r.status)) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Duyệt hoàn tiền</h1>
          <p className="text-neutral-500 mt-1">Xem xét và phê duyệt yêu cầu hoàn tiền</p>
        </div>
        <button
          onClick={() => setChatOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-xl hover:bg-primary-100 transition-colors"
        >
          <Sparkles size={18} className="text-primary-600" />
          <span className="font-medium text-primary-700">Hỏi AI</span>
        </button>
      </div>

      {/* Pending approvals alert */}
      {pendingRefunds.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-5 flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0">
            <AlertCircle className="text-red-600" size={24} />
          </div>
          <div>
            <h3 className="font-bold text-red-900">Có {pendingRefunds.length} yêu cầu đang chờ duyệt</h3>
            <p className="text-sm text-red-700 mt-1">Vui lòng xem xét và phê duyệt hoặc từ chối</p>
          </div>
        </div>
      )}

      {/* Info banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
        <AlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
        <div>
          <p className="font-medium text-blue-900">Lưu ý về quy trình hoàn tiền</p>
          <p className="text-sm text-blue-700 mt-1">
            Sau khi phê duyệt, bạn cần chuyển tiền thủ công vào tài khoản khách hàng. Sau đó đánh dấu đã hoàn tiền trong hệ thống.
          </p>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-card animate-pulse">
              <div className="h-32 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && refunds?.length === 0 && (
        <div className="bg-white rounded-2xl p-12 shadow-card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <RefreshCcw size={32} />
            </div>
            <p className="empty-state-title">Không có yêu cầu hoàn tiền nào</p>
            <p className="empty-state-description">Mọi thứ đang được xử lý tốt!</p>
          </div>
        </div>
      )}

      {/* Pending approvals */}
      {!isLoading && pendingRefunds.length > 0 && (
        <div>
          <h2 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <Clock className="text-amber-600" size={20} />
            Chờ phê duyệt ({pendingRefunds.length})
          </h2>
          <div className="space-y-4">
            {pendingRefunds.map((refund) => (
              <div key={refund.id} className="bg-white rounded-2xl p-6 shadow-card border-2 border-amber-200">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center flex-shrink-0">
                      <RefreshCcw className="text-amber-600" size={24} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-xl text-neutral-900">{refund.refund_code}</span>
                        <span className={`badge ${getStatusColor(refund.status)}`}>
                          {getStatusText(refund.status)}
                        </span>
                      </div>

                      <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500">Số tiền hoàn</p>
                          <p className="text-2xl font-bold text-primary-600">{formatCurrency(refund.amount)}</p>
                        </div>
                        <div className="bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500">Ngân hàng</p>
                          <p className="font-medium text-neutral-900">{refund.bank_name}</p>
                          <p className="text-sm text-neutral-600">{refund.account_number}</p>
                        </div>
                        <div className="bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500">Chủ tài khoản</p>
                          <p className="font-medium text-neutral-900">{refund.account_holder}</p>
                        </div>
                      </div>

                      {refund.reason && (
                        <div className="mt-4 bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500 mb-1">Lý do:</p>
                          <p className="text-neutral-700">{refund.reason}</p>
                        </div>
                      )}

                      {refund.complaint && (
                        <div className="mt-4 bg-orange-50 rounded-xl p-4 border border-orange-100">
                          <p className="text-sm text-orange-600 font-medium mb-1">Khiếu nại liên quan:</p>
                          <p className="text-neutral-700">{refund.complaint.description}</p>
                        </div>
                      )}

                      <p className="text-xs text-neutral-400 mt-4">{formatDateTime(refund.created_at)}</p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 pt-6 border-t border-neutral-100 flex gap-4">
                  <button
                    onClick={() => approveMutation.mutate(refund.id)}
                    disabled={approveMutation.isPending}
                    className="btn-success flex-1 py-3"
                  >
                    {approveMutation.isPending ? (
                      <span className="flex items-center gap-2">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Đang xử lý...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Check size={18} />
                        Phê duyệt
                      </span>
                    )}
                  </button>
                  <button
                    onClick={() => setRejectModal(refund.id)}
                    className="btn-danger px-6"
                  >
                    <X size={18} />
                    Từ chối
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Approved - waiting for transfer */}
      {!isLoading && approvedRefunds.length > 0 && (
        <div>
          <h2 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <Banknote className="text-green-600" size={20} />
            Đã duyệt - Chờ chuyển tiền ({approvedRefunds.length})
          </h2>
          <div className="space-y-4">
            {approvedRefunds.map((refund) => (
              <div key={refund.id} className="bg-white rounded-2xl p-6 shadow-card border-2 border-green-200">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center flex-shrink-0">
                      <Check className="text-green-600" size={24} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-xl text-neutral-900">{refund.refund_code}</span>
                        <span className={`badge ${getStatusColor(refund.status)}`}>
                          {getStatusText(refund.status)}
                        </span>
                      </div>

                      <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500">Số tiền hoàn</p>
                          <p className="text-2xl font-bold text-primary-600">{formatCurrency(refund.amount)}</p>
                        </div>
                        <div className="bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500">Ngân hàng</p>
                          <p className="font-medium text-neutral-900">{refund.bank_name}</p>
                          <p className="text-sm text-neutral-600">{refund.account_number}</p>
                        </div>
                        <div className="bg-neutral-50 rounded-xl p-4">
                          <p className="text-sm text-neutral-500">Chủ tài khoản</p>
                          <p className="font-medium text-neutral-900">{refund.account_holder}</p>
                        </div>
                      </div>

                      {refund.owner_note && (
                        <div className="mt-4 bg-blue-50 rounded-xl p-4 border border-blue-100">
                          <p className="text-sm text-blue-600 font-medium mb-1">Ghi chú của bạn:</p>
                          <p className="text-neutral-700">{refund.owner_note}</p>
                        </div>
                      )}

                      <p className="text-xs text-neutral-400 mt-4">{formatDateTime(refund.created_at)}</p>
                    </div>
                  </div>
                </div>

                {/* Action required */}
                <div className="mt-6 pt-6 border-t border-neutral-100">
                  <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-start gap-3 mb-4">
                    <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
                    <div>
                      <p className="font-medium text-green-900">Đã phê duyệt</p>
                      <p className="text-sm text-green-700 mt-1">
                        Vui lòng chuyển tiền vào tài khoản của khách hàng, sau đó đánh dấu đã hoàn tiền.
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => markRefundedMutation.mutate(refund.id)}
                    disabled={markRefundedMutation.isPending}
                    className="btn-primary w-full py-3"
                  >
                    {markRefundedMutation.isPending ? (
                      <span className="flex items-center gap-2">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Đang xử lý...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <CheckCircle size={18} />
                        Đánh dấu đã hoàn tiền
                      </span>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Other refunds (completed, rejected) */}
      {!isLoading && otherRefunds.length > 0 && (
        <div>
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Lịch sử hoàn tiền</h2>
          <div className="space-y-4">
            {otherRefunds.map((refund) => (
              <div key={refund.id} className="bg-white rounded-2xl p-5 shadow-card">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      refund.status === 'REFUNDED' ? 'bg-green-50' :
                      refund.status === 'REJECTED' ? 'bg-red-50' :
                      'bg-neutral-50'
                    }`}>
                      {refund.status === 'REFUNDED' ? (
                        <CheckCircle className="text-green-600" size={20} />
                      ) : refund.status === 'REJECTED' ? (
                        <X className="text-red-600" size={20} />
                      ) : (
                        <Clock className="text-neutral-400" size={20} />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-neutral-900">{refund.refund_code}</span>
                        <span className={`badge ${getStatusColor(refund.status)}`}>
                          {getStatusText(refund.status)}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-500 mt-1">{formatDateTime(refund.created_at)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-primary-600">{formatCurrency(refund.amount)}</p>
                    <p className="text-sm text-neutral-500">{refund.bank_name}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {rejectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4 shadow-elevated">
            <div className="text-center mb-6">
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <X className="text-red-600" size={32} />
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-2">Từ chối yêu cầu</h3>
              <p className="text-neutral-500">Vui lòng nhập lý do từ chối để thông báo cho khách hàng.</p>
            </div>

            <textarea
              value={rejectNote}
              onChange={(e) => setRejectNote(e.target.value)}
              placeholder="Nhập lý do từ chối..."
              rows={4}
              className="input resize-none mb-4"
            />

            <div className="flex gap-4">
              <button
                onClick={() => {
                  setRejectModal(null)
                  setRejectNote('')
                }}
                className="btn-secondary flex-1"
              >
                Hủy
              </button>
              <button
                onClick={() => rejectMutation.mutate({ id: rejectModal, note: rejectNote })}
                disabled={!rejectNote.trim() || rejectMutation.isPending}
                className="btn-danger flex-1"
              >
                {rejectMutation.isPending ? 'Đang xử lý...' : 'Xác nhận từ chối'}
              </button>
            </div>
          </div>
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
