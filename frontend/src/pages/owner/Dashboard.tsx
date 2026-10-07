import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import {
  Bus,
  Ticket,
  MessageSquare,
  RefreshCcw,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Sparkles,
  ArrowRight,
} from 'lucide-react'
import { dashboardApi, bookingApi } from '../../services/api'
import { formatCurrency, formatCurrencyShort } from '../../lib/utils'
import AIChat from '../../components/AIChat'

// Chart colors
const COLORS = {
  primary: '#0ea5e9',
  secondary: '#14b8a6',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  purple: '#a855f7',
  gray: '#64748b',
}

const STATUS_COLORS: Record<string, string> = {
  CONFIRMED: COLORS.success,
  PENDING_PAYMENT: COLORS.warning,
  CANCELLED: COLORS.danger,
}

const CHART_COLORS = [COLORS.primary, COLORS.success, COLORS.warning, COLORS.danger, COLORS.purple]

export default function OwnerDashboard() {
  const [chatOpen, setChatOpen] = useState(false)
  const [chartDays, setChartDays] = useState(7)

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats().then((res) => res.data),
  })

  const { data: chartData, isLoading: chartLoading } = useQuery({
    queryKey: ['chart-data', chartDays],
    queryFn: () => dashboardApi.getChartData(chartDays).then((res) => res.data),
  })

  const { data: recentBookings } = useQuery({
    queryKey: ['recent-bookings'],
    queryFn: () => bookingApi.getAllBookings().then((res) => res.data.slice(0, 5)),
  })

  const hasActionRequired = (stats?.pending_refunds || 0) > 0 || (stats?.open_complaints || 0) > 0

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-neutral-200">
          <p className="font-medium text-neutral-900">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.name === 'Doanh thu' ? formatCurrency(entry.value) : entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Tổng quan vận hành</h1>
          <p className="text-neutral-500 mt-1">Cập nhật real-time</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Time range selector */}
          <div className="bg-white rounded-lg border border-neutral-200 p-1 flex">
            {[7, 14, 30].map((days) => (
              <button
                key={days}
                onClick={() => setChartDays(days)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  chartDays === days
                    ? 'bg-primary-600 text-white'
                    : 'text-neutral-600 hover:bg-neutral-100'
                }`}
              >
                {days} ngày
              </button>
            ))}
          </div>
          <button
            onClick={() => setChatOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-xl hover:bg-primary-100 transition-colors"
          >
            <Sparkles size={18} className="text-primary-600" />
            <span className="font-medium text-primary-700">AI</span>
          </button>
        </div>
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

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          icon={Bus}
          iconColor="bg-blue-50 text-blue-600"
          label="Tổng chuyến"
          value={stats?.total_trips || 0}
          subValue={`${stats?.today_trips || 0} hôm nay`}
          isLoading={statsLoading}
        />
        <KpiCard
          icon={Ticket}
          iconColor="bg-green-50 text-green-600"
          label="Tổng booking"
          value={stats?.total_bookings || 0}
          subValue={`${stats?.today_bookings || 0} hôm nay`}
          isLoading={statsLoading}
        />
        <KpiCard
          icon={TrendingUp}
          iconColor="bg-purple-50 text-purple-600"
          label="Doanh thu"
          value={formatCurrencyShort(stats?.revenue || 0)}
          subValue="Tổng"
          isLoading={statsLoading}
          isText
        />
        <KpiCard
          icon={MessageSquare}
          iconColor="bg-orange-50 text-orange-600"
          label="Khiếu nại mở"
          value={stats?.open_complaints || 0}
          subValue=""
          isLoading={statsLoading}
          link="/owner/complaints"
        />
        <KpiCard
          icon={RefreshCcw}
          iconColor="bg-red-50 text-red-600"
          label="Hoàn tiền chờ"
          value={stats?.pending_refunds || 0}
          subValue=""
          isLoading={statsLoading}
          link="/owner/approvals"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Booking Trend - Line Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-lg text-neutral-900">Booking theo thời gian</h3>
              <p className="text-sm text-neutral-500">Số lượng booking trong {chartDays} ngày</p>
            </div>
          </div>
          {chartLoading ? (
            <div className="h-64 bg-neutral-50 rounded-xl animate-pulse" />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={chartData?.bookings_by_day}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Booking"
                  stroke={COLORS.primary}
                  strokeWidth={3}
                  dot={{ fill: COLORS.primary, strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, fill: COLORS.primary }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Booking Status - Pie Chart */}
        <div className="bg-white rounded-2xl p-6 shadow-card">
          <div className="mb-6">
            <h3 className="font-bold text-lg text-neutral-900">Trạng thái Booking</h3>
            <p className="text-sm text-neutral-500">Tỷ lệ theo trạng thái</p>
          </div>
          {chartLoading ? (
            <div className="h-64 bg-neutral-50 rounded-xl animate-pulse" />
          ) : chartData?.bookings_by_status && chartData.bookings_by_status.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={chartData.bookings_by_status}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="count"
                  >
                    {chartData.bookings_by_status.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={STATUS_COLORS[entry.status] || CHART_COLORS[index % CHART_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-4">
                {chartData.bookings_by_status.map((item, index) => (
                  <div key={item.status} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{
                          backgroundColor:
                            STATUS_COLORS[item.status] || CHART_COLORS[index % CHART_COLORS.length],
                        }}
                      />
                      <span className="text-sm text-neutral-600">
                        {item.status === 'CONFIRMED'
                          ? 'Đã xác nhận'
                          : item.status === 'PENDING_PAYMENT'
                          ? 'Chờ thanh toán'
                          : 'Đã hủy'}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-neutral-900">
                      {item.count} ({item.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-neutral-400">
              Chưa có dữ liệu
            </div>
          )}
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Revenue Chart - Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-lg text-neutral-900">Doanh thu theo ngày</h3>
              <p className="text-sm text-neutral-500">Biến động doanh thu trong {chartDays} ngày</p>
            </div>
          </div>
          {chartLoading ? (
            <div className="h-64 bg-neutral-50 rounded-xl animate-pulse" />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData?.revenue_by_day}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis
                  tick={{ fontSize: 12 }}
                  stroke="#94a3b8"
                  tickFormatter={(value) => formatCurrencyShort(value)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="revenue" name="Doanh thu" fill={COLORS.secondary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Bookings by Route */}
        <div className="bg-white rounded-2xl p-6 shadow-card">
          <div className="mb-6">
            <h3 className="font-bold text-lg text-neutral-900">Booking theo tuyến</h3>
            <p className="text-sm text-neutral-500">Top 5 tuyến phổ biến</p>
          </div>
          {chartLoading ? (
            <div className="h-64 bg-neutral-50 rounded-xl animate-pulse" />
          ) : chartData?.bookings_by_route && chartData.bookings_by_route.length > 0 ? (
            <div className="space-y-3">
              {chartData.bookings_by_route.map((route, index) => {
                const maxCount = Math.max(...chartData.bookings_by_route.map((r) => r.count))
                const percentage = maxCount > 0 ? (route.count / maxCount) * 100 : 0
                return (
                  <div key={route.route}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-neutral-900 truncate max-w-[180px]">
                        {route.origin} → {route.destination}
                      </span>
                      <span className="text-sm font-semibold text-neutral-900">{route.count}</span>
                    </div>
                    <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${percentage}%`,
                          backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
                        }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-neutral-400">
              Chưa có dữ liệu
            </div>
          )}
        </div>
      </div>

      {/* Recent Bookings */}
      <div className="bg-white rounded-2xl p-6 shadow-card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-lg text-neutral-900">Booking gần đây</h3>
            <p className="text-sm text-neutral-500">Các booking mới nhất</p>
          </div>
          <Link
            to="/owner/bookings"
            className="flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Xem tất cả <ArrowRight size={16} />
          </Link>
        </div>
        {recentBookings && recentBookings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-100">
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">Mã</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">Số ghế</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">Tổng tiền</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {recentBookings.map((booking) => (
                  <tr key={booking.id} className="border-b border-neutral-50 hover:bg-neutral-50">
                    <td className="py-3 px-4 font-medium text-neutral-900">{booking.booking_code}</td>
                    <td className="py-3 px-4 text-neutral-600">{booking.seat_count} ghế</td>
                    <td className="py-3 px-4 font-medium text-neutral-900">{formatCurrency(booking.total_amount)}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={booking.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-12 text-center text-neutral-400">Chưa có booking nào</div>
        )}
      </div>

      {/* Status indicator */}
      <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle className="text-green-600" size={20} />
          <div>
            <p className="font-medium text-green-900">Hệ thống hoạt động tốt</p>
            <p className="text-sm text-green-700">Mọi thứ đang được giám sát</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-green-700 font-medium">Online</span>
        </div>
      </div>

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

// KPI Card Component
function KpiCard({
  icon: Icon,
  iconColor,
  label,
  value,
  subValue,
  isLoading,
  isText,
  link,
}: {
  icon: any
  iconColor: string
  label: string
  value: number | string
  subValue: string
  isLoading?: boolean
  isText?: boolean
  link?: string
}) {
  const content = (
    <div className={`bg-white rounded-xl p-5 border border-neutral-100 hover:shadow-soft transition-all ${link ? 'cursor-pointer' : ''}`}>
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconColor}`}>
          <Icon size={20} />
        </div>
      </div>
      {isLoading ? (
        <div className="h-8 bg-neutral-100 rounded animate-pulse w-20" />
      ) : (
        <p className={`font-bold text-neutral-900 ${isText ? 'text-xl' : 'text-2xl'}`}>{value}</p>
      )}
      <p className="text-sm text-neutral-500 mt-1">{label}</p>
      {subValue && <p className="text-xs text-neutral-400 mt-0.5">{subValue}</p>}
    </div>
  )

  if (link) {
    return <Link to={link}>{content}</Link>
  }
  return content
}

// Status Badge Component
function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    CONFIRMED: { bg: 'bg-green-50', text: 'text-green-700', label: 'Đã xác nhận' },
    PENDING_PAYMENT: { bg: 'bg-amber-50', text: 'text-amber-700', label: 'Chờ thanh toán' },
    CANCELLED: { bg: 'bg-red-50', text: 'text-red-700', label: 'Đã hủy' },
  }

  const { bg, text, label } = config[status] || { bg: 'bg-neutral-50', text: 'text-neutral-700', label: status }

  return (
    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${bg} ${text}`}>
      {label}
    </span>
  )
}
