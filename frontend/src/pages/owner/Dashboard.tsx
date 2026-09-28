import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Bus,
  Ticket,
  CreditCard,
  MessageSquare,
  RefreshCcw,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Sparkles,
  ArrowRight,
  DollarSign,
  Calendar,
} from 'lucide-react'
import { dashboardApi, refundApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'
import AIChat from '../../components/AIChat'
import { useState } from 'react'

export default function OwnerDashboard() {
  const [chatOpen, setChatOpen] = useState(false)

  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats().then((res) => res.data),
  })

  useQuery({
    queryKey: ['pending-refunds-dashboard'],
    queryFn: () => refundApi.getPendingRefunds().then((res) => res.data),
  })

  const hasActionRequired = (stats?.pending_refunds || 0) > 0 || (stats?.open_complaints || 0) > 0

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-32 bg-neutral-100 rounded-2xl animate-pulse" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-neutral-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Dashboard</h1>
          <p className="text-neutral-500 mt-1">Trung tâm điều hành vận hành</p>
        </div>
        <button
          onClick={() => setChatOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-50 to-accent-50 border border-primary-200 rounded-xl hover:from-primary-100 hover:to-accent-100 transition-colors"
        >
          <Sparkles size={18} className="text-primary-600" />
          <span className="font-medium text-primary-700">AI Assistant</span>
        </button>
      </div>

      {/* Action Required Banner */}
      {hasActionRequired && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-2xl p-5">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="text-red-600" size={24} />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-red-900 text-lg">Cần xử lý ngay</h3>
              <div className="mt-3 space-y-2">
                {(stats?.pending_refunds || 0) > 0 && (
                  <Link
                    to="/owner/approvals"
                    className="flex items-center justify-between bg-white rounded-xl p-3 hover:shadow-soft transition-shadow"
                  >
                    <div className="flex items-center gap-3">
                      <RefreshCcw className="text-red-600" size={20} />
                      <div>
                        <p className="font-medium text-neutral-900">{stats?.pending_refunds} yêu cầu hoàn tiền</p>
                        <p className="text-sm text-neutral-500">Chờ bạn phê duyệt</p>
                      </div>
                    </div>
                    <span className="text-primary-600 font-medium text-sm flex items-center gap-1">
                      Xử lý <ArrowRight size={16} />
                    </span>
                  </Link>
                )}
                {(stats?.open_complaints || 0) > 0 && (
                  <Link
                    to="/owner/complaints"
                    className="flex items-center justify-between bg-white rounded-xl p-3 hover:shadow-soft transition-shadow"
                  >
                    <div className="flex items-center gap-3">
                      <MessageSquare className="text-orange-600" size={20} />
                      <div>
                        <p className="font-medium text-neutral-900">{stats?.open_complaints} khiếu nại mới</p>
                        <p className="text-sm text-neutral-500">Cần được xử lý</p>
                      </div>
                    </div>
                    <span className="text-primary-600 font-medium text-sm flex items-center gap-1">
                      Xem ngay <ArrowRight size={16} />
                    </span>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
              <Calendar className="text-blue-600" size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{stats?.today_trips || 0}</p>
              <p className="text-sm text-neutral-500">Chuyến hôm nay</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center">
              <Ticket className="text-green-600" size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{stats?.today_bookings || 0}</p>
              <p className="text-sm text-neutral-500">Booking hôm nay</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center">
              <TrendingUp className="text-purple-600" size={22} />
            </div>
            <div>
              <p className="text-xl font-bold text-purple-600">{formatCurrency(stats?.revenue || 0)}</p>
              <p className="text-sm text-neutral-500">Doanh thu</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center">
              <CreditCard className="text-amber-600" size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{stats?.pending_payments || 0}</p>
              <p className="text-sm text-neutral-500">Chờ thanh toán</p>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary stats */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
        <Link
          to="/owner/trips"
          className="bg-white rounded-xl p-4 border border-neutral-100 hover:border-blue-200 hover:shadow-soft transition-all"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center mb-3">
            <Bus className="text-blue-600" size={18} />
          </div>
          <p className="text-xl font-bold text-neutral-900">{stats?.total_trips || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">Tổng chuyến</p>
        </Link>
        <Link
          to="/owner/bookings"
          className="bg-white rounded-xl p-4 border border-neutral-100 hover:border-green-200 hover:shadow-soft transition-all"
        >
          <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center mb-3">
            <Ticket className="text-green-600" size={18} />
          </div>
          <p className="text-xl font-bold text-neutral-900">{stats?.total_bookings || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">Tổng booking</p>
        </Link>
        <Link
          to="/owner/complaints"
          className="bg-white rounded-xl p-4 border border-neutral-100 hover:border-orange-200 hover:shadow-soft transition-all"
        >
          <div className="w-10 h-10 rounded-lg bg-orange-50 flex items-center justify-center mb-3">
            <MessageSquare className="text-orange-600" size={18} />
          </div>
          <p className="text-xl font-bold text-neutral-900">{stats?.open_complaints || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">Khiếu nại mở</p>
        </Link>
        <Link
          to="/owner/approvals"
          className="bg-white rounded-xl p-4 border border-neutral-100 hover:border-red-200 hover:shadow-soft transition-all"
        >
          <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center mb-3">
            <RefreshCcw className="text-red-600" size={18} />
          </div>
          <p className="text-xl font-bold text-neutral-900">{stats?.pending_refunds || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">Hoàn tiền chờ</p>
        </Link>
        <div className="bg-white rounded-xl p-4 border border-neutral-100">
          <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center mb-3">
            <DollarSign className="text-purple-600" size={18} />
          </div>
          <p className="text-xl font-bold text-neutral-900">{stats?.revenue || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">Doanh thu (số)</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-neutral-100">
          <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center mb-3">
            <CheckCircle className="text-green-600" size={18} />
          </div>
          <p className="text-xl font-bold text-neutral-900">
            {(stats?.total_bookings || 0) - (stats?.pending_payments || 0)}
          </p>
          <p className="text-xs text-neutral-500 mt-1">Đã thanh toán</p>
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/owner/trips"
          className="bg-white rounded-xl p-5 border border-neutral-100 hover:shadow-soft transition-shadow"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
              <Bus className="text-blue-600" size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Quản lý chuyến xe</h3>
              <p className="text-sm text-neutral-500 mt-0.5">Thêm, sửa, xóa chuyến</p>
            </div>
          </div>
        </Link>
        <Link
          to="/owner/bookings"
          className="bg-white rounded-xl p-5 border border-neutral-100 hover:shadow-soft transition-shadow"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center">
              <Ticket className="text-green-600" size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Xem đặt vé</h3>
              <p className="text-sm text-neutral-500 mt-0.5">Danh sách booking</p>
            </div>
          </div>
        </Link>
        <Link
          to="/owner/complaints"
          className="bg-white rounded-xl p-5 border border-neutral-100 hover:shadow-soft transition-shadow"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center">
              <MessageSquare className="text-orange-600" size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Khiếu nại</h3>
              <p className="text-sm text-neutral-500 mt-0.5">Xử lý khiếu nại</p>
            </div>
          </div>
        </Link>
        <Link
          to="/owner/approvals"
          className="bg-white rounded-xl p-5 border border-neutral-100 hover:shadow-soft transition-shadow"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center">
              <RefreshCcw className="text-red-600" size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Duyệt hoàn tiền</h3>
              <p className="text-sm text-neutral-500 mt-0.5">Phê duyệt refund</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Status indicator */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
          <CheckCircle className="text-green-600" size={20} />
        </div>
        <div>
          <p className="font-medium text-green-900">Hệ thống hoạt động tốt</p>
          <p className="text-sm text-green-700">Mọi thứ đang được giám sát</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-green-700">Online</span>
        </div>
      </div>

      {/* AI Chat Modal */}
      {chatOpen && (
        <div className="fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-black/30"
            onClick={() => setChatOpen(false)}
          />
          <div className="absolute bottom-0 right-0 w-full h-[calc(100vh-4rem)] lg:w-96 lg:h-[32rem] lg:rounded-t-2xl shadow-elevated">
            <AIChat
              context="owner"
              embedded
              onClose={() => setChatOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}
