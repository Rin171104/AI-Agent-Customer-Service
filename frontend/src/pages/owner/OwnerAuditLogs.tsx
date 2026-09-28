import { useQuery } from '@tanstack/react-query'
import { FileText, Sparkles, Clock, User, Bot } from 'lucide-react'
import { auditApi } from '../../services/api'
import { formatDateTime } from '../../lib/utils'
import AIChat from '../../components/AIChat'
import { useState } from 'react'

export default function OwnerAuditLogs() {
  const [chatOpen, setChatOpen] = useState(false)

  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => auditApi.getLogs({ limit: 200 }).then((res) => res.data),
  })

  const getActionColor = (action: string) => {
    if (action.includes('APPROVE') || action.includes('SUCCESS')) return 'badge-success'
    if (action.includes('REJECT') || action.includes('FAIL') || action.includes('CANCEL')) return 'badge-danger'
    if (action.includes('CREATE')) return 'badge-info'
    if (action.includes('UPDATE')) return 'badge-warning'
    if (action.includes('REFUND')) return 'bg-purple-50 text-purple-700 border border-purple-200'
    return 'badge-neutral'
  }

  const getActorIcon = (actorType: string) => {
    if (actorType === 'OWNER') return <User size={14} />
    if (actorType === 'CUSTOMER') return <User size={14} />
    return <Bot size={14} />
  }

  const getActorColor = (actorType: string) => {
    if (actorType === 'OWNER') return 'bg-purple-50 text-purple-700 border border-purple-200'
    if (actorType === 'CUSTOMER') return 'bg-blue-50 text-blue-700 border border-blue-200'
    return 'bg-neutral-50 text-neutral-700 border border-neutral-200'
  }

  const getActorLabel = (actorType: string) => {
    if (actorType === 'OWNER') return 'Chủ nhà xe'
    if (actorType === 'CUSTOMER') return 'Khách hàng'
    return 'Hệ thống'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Audit Logs</h1>
          <p className="text-neutral-500 mt-1">Nhật ký hoạt động trên hệ thống</p>
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
        <div className="bg-white rounded-xl p-4 border border-neutral-100 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
            <User size={18} className="text-purple-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-neutral-900">
              {logs?.filter((l) => l.actor_type === 'OWNER').length || 0}
            </p>
            <p className="text-sm text-neutral-500">Từ Owner</p>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-neutral-100 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
            <User size={18} className="text-blue-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-neutral-900">
              {logs?.filter((l) => l.actor_type === 'CUSTOMER').length || 0}
            </p>
            <p className="text-sm text-neutral-500">Từ Customer</p>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-neutral-100 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neutral-50 flex items-center justify-center">
            <Bot size={18} className="text-neutral-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-neutral-900">
              {logs?.filter((l) => l.actor_type === 'SYSTEM').length || 0}
            </p>
            <p className="text-sm text-neutral-500">Từ hệ thống</p>
          </div>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-card animate-pulse">
              <div className="h-12 bg-neutral-100 rounded-lg" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && logs?.length === 0 && (
        <div className="bg-white rounded-2xl p-12 shadow-card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <FileText size={32} />
            </div>
            <p className="empty-state-title">Chưa có nhật ký nào</p>
            <p className="empty-state-description">Các hoạt động sẽ được ghi lại tại đây</p>
          </div>
        </div>
      )}

      {/* Logs list */}
      {!isLoading && logs && logs.length > 0 && (
        <div className="space-y-3">
          {logs.map((log) => (
            <div
              key={log.id}
              className="bg-white rounded-xl p-4 shadow-card hover:shadow-soft transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getActorColor(log.actor_type)}`}>
                  {getActorIcon(log.actor_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${getActorColor(log.actor_type)}`}>
                      {getActorLabel(log.actor_type)}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${getActionColor(log.action)}`}>
                      {log.action}
                    </span>
                    <span className="text-sm text-neutral-500">
                      {log.entity_type}
                      {log.entity_id && <span className="text-neutral-400 ml-1">#{log.entity_id.slice(0, 8)}</span>}
                    </span>
                  </div>
                  {log.description && (
                    <p className="text-sm text-neutral-700">{log.description}</p>
                  )}
                  <div className="flex items-center gap-1 mt-2 text-xs text-neutral-400">
                    <Clock size={12} />
                    {formatDateTime(log.created_at)}
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
            <AIChat context="owner" embedded onClose={() => setChatOpen(false)} />
          </div>
        </div>
      )}
    </div>
  )
}
