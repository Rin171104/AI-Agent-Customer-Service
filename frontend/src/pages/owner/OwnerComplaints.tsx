import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MessageSquare } from 'lucide-react'
import { complaintApi } from '../../services/api'
import { formatDateTime, getStatusColor, getStatusText } from '../../lib/utils'

const complaintTypes = [
  { value: 'WRONG_SEAT', label: 'Ghế không đúng' },
  { value: 'LATE', label: 'Xe trễ giờ' },
  { value: 'DRIVER', label: 'Vấn đề tài xế' },
  { value: 'LOST_ITEM', label: 'Mất đồ' },
  { value: 'PAYMENT', label: 'Vấn đề thanh toán' },
  { value: 'BOOKING_ERROR', label: 'Lỗi đặt vé' },
  { value: 'OTHER', label: 'Khác' },
]

export default function OwnerComplaints() {
  const queryClient = useQueryClient()

  const { data: complaints, isLoading } = useQuery({
    queryKey: ['all-complaints'],
    queryFn: () => complaintApi.getAllComplaints().then((res) => res.data),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { status?: string; owner_note?: string } }) =>
      complaintApi.update(id, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-complaints'] })
    },
  })

  const resolveMutation = useMutation({
    mutationFn: ({ id, note }: { id: string; note: string }) =>
      complaintApi.resolve(id, note).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-complaints'] })
    },
  })

  const handleResolve = (id: string) => {
    const note = prompt('Nhập ghi chú giải quyết:')
    if (note) {
      resolveMutation.mutate({ id, note })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Quản lý khiếu nại</h1>
        <p className="text-gray-500 mt-1">Xem và xử lý khiếu nại từ khách hàng</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-blue-600">
            {complaints?.filter((c) => c.status === 'OPEN').length || 0}
          </p>
          <p className="text-sm text-blue-700">Mới</p>
        </div>
        <div className="bg-orange-50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-orange-600">
            {complaints?.filter((c) => c.status === 'IN_PROGRESS').length || 0}
          </p>
          <p className="text-sm text-orange-700">Đang xử lý</p>
        </div>
        <div className="bg-green-50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-green-600">
            {complaints?.filter((c) => c.status === 'RESOLVED').length || 0}
          </p>
          <p className="text-sm text-green-700">Đã giải quyết</p>
        </div>
      </div>

      {/* Complaints List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : complaints?.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <MessageSquare className="mx-auto mb-3 text-gray-300" size={64} />
          <p className="text-lg">Không có khiếu nại nào</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {complaints?.map((complaint) => (
            <div key={complaint.id} className="bg-white rounded-xl p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
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
                    <span className="text-gray-500 text-sm">
                      {complaintTypes.find((t) => t.value === complaint.type)?.label}
                    </span>
                  </div>
                  <p className="text-gray-700 mt-3">{complaint.description}</p>
                  {complaint.booking && (
                    <p className="text-sm text-gray-500 mt-2">
                      Booking: {complaint.booking.booking_code} - {complaint.booking.seat_count} ghế
                    </p>
                  )}
                  {complaint.owner_note && (
                    <div className="mt-3 bg-gray-50 rounded-lg p-3">
                      <p className="text-sm text-gray-500">Phản hồi của bạn:</p>
                      <p className="text-gray-700">{complaint.owner_note}</p>
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-3">{formatDateTime(complaint.created_at)}</p>
                </div>

                <div className="flex gap-2 ml-4">
                  {complaint.status === 'OPEN' && (
                    <button
                      onClick={() => updateMutation.mutate({ id: complaint.id, data: { status: 'IN_PROGRESS' } })}
                      className="px-4 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium hover:bg-orange-700"
                    >
                      Tiếp nhận
                    </button>
                  )}
                  {complaint.status === 'IN_PROGRESS' && (
                    <button
                      onClick={() => handleResolve(complaint.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
                    >
                      Giải quyết
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
