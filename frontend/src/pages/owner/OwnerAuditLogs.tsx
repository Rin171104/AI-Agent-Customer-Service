import { useQuery } from '@tanstack/react-query'
import { FileText } from 'lucide-react'
import { auditApi } from '../../services/api'
import { formatDateTime } from '../../lib/utils'

export default function OwnerAuditLogs() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => auditApi.getLogs({ limit: 200 }).then((res) => res.data),
  })

  const getActionColor = (action: string) => {
    if (action.includes('APPROVE') || action.includes('SUCCESS')) return 'bg-green-100 text-green-800'
    if (action.includes('REJECT') || action.includes('FAIL') || action.includes('CANCEL')) return 'bg-red-100 text-red-800'
    if (action.includes('CREATE')) return 'bg-blue-100 text-blue-800'
    if (action.includes('UPDATE')) return 'bg-yellow-100 text-yellow-800'
    if (action.includes('REFUND')) return 'bg-purple-100 text-purple-800'
    return 'bg-gray-100 text-gray-800'
  }

  const getActorLabel = (actorType: string) => {
    if (actorType === 'OWNER') return 'Chủ nhà xe'
    if (actorType === 'CUSTOMER') return 'Khách hàng'
    return 'Hệ thống'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <p className="text-gray-500 mt-1">Nhật ký hoạt động trên hệ thống</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        </div>
      ) : logs?.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center text-gray-500">
          <FileText className="mx-auto mb-3 text-gray-300" size={64} />
          <p className="text-lg">Chưa có nhật ký nào</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thời gian</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hành động</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mô tả</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {logs?.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-600 whitespace-nowrap">
                      {formatDateTime(log.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        log.actor_type === 'OWNER' ? 'bg-purple-100 text-purple-800' :
                        log.actor_type === 'CUSTOMER' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {getActorLabel(log.actor_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {log.entity_type}
                      {log.entity_id && <span className="text-gray-400 ml-1">#{log.entity_id.slice(0, 8)}</span>}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                      {log.description || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
