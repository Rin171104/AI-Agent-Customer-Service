import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Bus, Ticket, MessageSquare, RefreshCcw, FileText, LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../services/auth'

const customerNavItems = [
  { to: '/customer', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/customer/trips', label: 'Tìm chuyến', icon: Bus },
  { to: '/customer/bookings', label: 'Đặt vé của tôi', icon: Ticket },
  { to: '/customer/complaints', label: 'Khiếu nại', icon: MessageSquare },
  { to: '/customer/refunds', label: 'Hoàn tiền', icon: RefreshCcw },
]

const ownerNavItems = [
  { to: '/owner', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/owner/trips', label: 'Chuyến xe', icon: Bus },
  { to: '/owner/bookings', label: 'Đặt vé', icon: Ticket },
  { to: '/owner/complaints', label: 'Khiếu nại', icon: MessageSquare },
  { to: '/owner/approvals', label: 'Duyệt hoàn tiền', icon: RefreshCcw },
  { to: '/owner/audit', label: 'Audit Log', icon: FileText },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navItems = user?.role === 'OWNER' ? ownerNavItems : customerNavItems

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b flex items-center px-4 z-30">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className="ml-4 font-semibold text-lg">Hiền Hựu Bus</div>
      </div>

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
      >
        <div className="p-6">
          <h1 className="text-xl font-bold text-white">Hiền Hựu Bus</h1>
          <p className="text-sm text-gray-400 mt-1">Quản lý nhà xe</p>
        </div>

        <nav className="px-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/customer' || item.to === '/owner'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-300 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-4 px-4">
            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{user?.name}</p>
              <p className="text-xs text-gray-400">{user?.role === 'OWNER' ? 'Chủ nhà xe' : 'Khách hàng'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-2 text-gray-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"
          >
            <LogOut size={20} />
            <span>Đăng xuất</span>
          </button>
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="lg:ml-64 pt-16 lg:pt-0 min-h-screen">
        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
