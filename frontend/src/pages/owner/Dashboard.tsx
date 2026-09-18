import { useQuery } from '@tanstack/react-query'
import { Bus, Ticket, CreditCard, MessageSquare, RefreshCcw, TrendingUp, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import { dashboardApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'

export default function OwnerDashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats().then((res) => res.data),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  const statCards = [
    {
      label: 'Tổng chuyến xe',
      value: stats?.total_trips || 0,
      icon: Bus,
      color: 'bg-blue-500',
      link: '/owner/trips',
    },
    {
      label: 'Đặt vé hôm nay',
      value: stats?.today_bookings || 0,
      icon: Ticket,
      color: 'bg-green-500',
      link: '/owner/bookings',
    },
    {
      label: 'Doanh thu',
      value: formatCurrency(stats?.revenue || 0),
      icon: TrendingUp,
      color: 'bg-purple-500',
      isText: true,
    },
    {
      label: 'Chờ thanh toán',
      value: stats?.pending_payments || 0,
      icon: CreditCard,
      color: 'bg-yellow-500',
      link: '/owner/bookings',
    },
    {
      label: 'Khiếu nại mở',
      value: stats?.open_complaints || 0,
      icon: MessageSquare,
      color: 'bg-orange-500',
      link: '/owner/complaints',
    },
    {
      label: 'Chờ duyệt hoàn tiền',
      value: stats?.pending_refunds || 0,
      icon: RefreshCcw,
      color: 'bg-red-500',
      link: '/owner/approvals',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Tổng quan tình hình vận hành</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((card, index) => (
          <Link
            key={index}
            to={card.link || '#'}
            className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className={`w-10 h-10 ${card.color} rounded-lg flex items-center justify-center mb-3`}>
              <card.icon className="text-white" size={20} />
            </div>
            {card.isText ? (
              <p className="text-lg font-bold text-gray-900 truncate">{card.value}</p>
            ) : (
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            )}
            <p className="text-sm text-gray-500 mt-1">{card.label}</p>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Hành động nhanh</h2>
          <div className="grid grid-cols-2 gap-4">
            <Link
              to="/owner/trips"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Bus className="text-primary-600" size={24} />
              <span className="font-medium">Quản lý chuyến xe</span>
            </Link>
            <Link
              to="/owner/bookings"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Ticket className="text-green-600" size={24} />
              <span className="font-medium">Xem đặt vé</span>
            </Link>
            <Link
              to="/owner/approvals"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <RefreshCcw className="text-red-600" size={24} />
              <span className="font-medium">Duyệt hoàn tiền</span>
            </Link>
            <Link
              to="/owner/audit"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Users className="text-purple-600" size={24} />
              <span className="font-medium">Audit Log</span>
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Cảnh báo</h2>
          <div className="space-y-3">
            {(stats?.pending_refunds || 0) > 0 && (
              <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
                <RefreshCcw className="text-red-600" size={20} />
                <span className="text-red-800">{(stats?.pending_refunds || 0)} yêu cầu hoàn tiền đang chờ duyệt</span>
              </div>
            )}
            {(stats?.open_complaints || 0) > 0 && (
              <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                <MessageSquare className="text-orange-600" size={20} />
                <span className="text-orange-800">{(stats?.open_complaints || 0)} khiếu nại chưa xử lý</span>
              </div>
            )}
            {(stats?.pending_payments || 0) > 0 && (
              <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
                <CreditCard className="text-yellow-600" size={20} />
                <span className="text-yellow-800">{(stats?.pending_payments || 0)} thanh toán đang chờ</span>
              </div>
            )}
            {(stats?.pending_refunds || 0) === 0 && (stats?.open_complaints || 0) === 0 && (stats?.pending_payments || 0) === 0 && (
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <TrendingUp className="text-green-600" size={20} />
                <span className="text-green-800">Mọi thứ hoạt động tốt!</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
