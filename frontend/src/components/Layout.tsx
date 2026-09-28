import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  Ticket,
  MessageSquare,
  RefreshCcw,
  FileText,
  LogOut,
  Menu,
  X,
  Sparkles,
  Bot,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../services/auth'
import AIChat from './AIChat'

// Customer navigation items
const customerNavItems = [
  { to: '/customer', label: 'Tổng quan', icon: LayoutDashboard },
  { to: '/customer/trips', label: 'Tìm chuyến', icon: Search },
  { to: '/customer/bookings', label: 'Vé của tôi', icon: Ticket },
  { to: '/customer/complaints', label: 'Khiếu nại', icon: MessageSquare },
  { to: '/customer/refunds', label: 'Hoàn tiền', icon: RefreshCcw },
]

// Owner navigation items
const ownerNavItems = [
  { to: '/owner', label: 'Tổng quan', icon: LayoutDashboard },
  { to: '/owner/trips', label: 'Chuyến xe', icon: Search },
  { to: '/owner/bookings', label: 'Đặt vé', icon: Ticket },
  { to: '/owner/complaints', label: 'Khiếu nại', icon: MessageSquare },
  { to: '/owner/approvals', label: 'Hoàn tiền', icon: RefreshCcw },
  { to: '/owner/audit', label: 'Audit Log', icon: FileText },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const isOwner = user?.role === 'OWNER'
  const navItems = isOwner ? ownerNavItems : customerNavItems

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-neutral-100
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:z-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-neutral-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center">
              <Bot className="text-white" size={18} />
            </div>
            <div>
              <h1 className="font-bold text-neutral-900">Hiền Hựu</h1>
              <p className="text-xs text-neutral-500">{isOwner ? 'Owner Dashboard' : 'Customer'}</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-neutral-100 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/customer' || item.to === '/owner'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 font-medium'
                    : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
                }`
              }
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* AI Chat trigger in sidebar */}
        <div className="px-4 mt-4">
          <button
            onClick={() => {
              setSidebarOpen(false)
              setChatOpen(true)
            }}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl bg-gradient-to-r from-primary-50 to-accent-50 text-primary-700 hover:from-primary-100 hover:to-accent-100 transition-all duration-200"
          >
            <Sparkles size={20} />
            <span className="font-medium">AI Assistant</span>
            <span className="ml-auto w-2 h-2 rounded-full bg-green-500" />
          </button>
        </div>

        {/* User section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-neutral-100 bg-white">
          <div className="flex items-center gap-3 mb-3 px-1">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-neutral-900 truncate">{user?.name}</p>
              <p className="text-xs text-neutral-500">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 rounded-xl transition-colors"
          >
            <LogOut size={18} />
            <span className="font-medium">Đăng xuất</span>
          </button>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="lg:hidden h-16 bg-white border-b border-neutral-100 flex items-center justify-between px-4 sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-neutral-100 rounded-lg"
            >
              <Menu size={24} />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center">
                <Bot className="text-white" size={14} />
              </div>
              <span className="font-bold text-neutral-900">Hiền Hựu</span>
            </div>
          </div>
          <button
            onClick={() => setChatOpen(true)}
            className="p-2 hover:bg-neutral-100 rounded-lg"
          >
            <Sparkles size={24} className="text-primary-600" />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <Outlet />
        </main>
      </div>

      {/* AI Chat Modal */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 lg:bottom-6 lg:right-6 lg:inset-auto">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/30 lg:hidden"
            onClick={() => setChatOpen(false)}
          />
          {/* Chat */}
          <AIChat
            context={isOwner ? 'owner' : 'customer'}
            embedded
            onClose={() => setChatOpen(false)}
            className="absolute bottom-0 right-0 w-full h-[calc(100vh-4rem)] lg:w-96 lg:h-[32rem] lg:rounded-2xl shadow-elevated"
          />
        </div>
      )}
    </div>
  )
}
