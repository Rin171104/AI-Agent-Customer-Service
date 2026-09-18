import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './services/auth'
import Layout from './components/Layout'
import AuthLayout from './components/AuthLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CustomerDashboard from './pages/customer/Dashboard'
import SearchTrips from './pages/customer/SearchTrips'
import TripDetail from './pages/customer/TripDetail'
import MyBookings from './pages/customer/MyBookings'
import BookingDetail from './pages/customer/BookingDetail'
import MyComplaints from './pages/customer/MyComplaints'
import MyRefunds from './pages/customer/MyRefunds'
import OwnerDashboard from './pages/owner/Dashboard'
import OwnerTrips from './pages/owner/OwnerTrips'
import OwnerBookings from './pages/owner/OwnerBookings'
import OwnerComplaints from './pages/owner/OwnerComplaints'
import OwnerApprovals from './pages/owner/OwnerApprovals'
import OwnerAuditLogs from './pages/owner/OwnerAuditLogs'

function ProtectedRoute({ children, allowedRole }: { children: React.ReactNode; allowedRole?: 'CUSTOMER' | 'OWNER' }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRole && user.role !== allowedRole) {
    return <Navigate to={user.role === 'OWNER' ? '/owner' : '/customer'} replace />
  }

  return <>{children}</>
}

export default function App() {
  const { user, isLoading } = useAuth()

  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Customer Routes */}
      <Route
        element={
          <ProtectedRoute allowedRole="CUSTOMER">
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/customer" element={<CustomerDashboard />} />
        <Route path="/customer/trips" element={<SearchTrips />} />
        <Route path="/customer/trips/:tripId" element={<TripDetail />} />
        <Route path="/customer/bookings" element={<MyBookings />} />
        <Route path="/customer/bookings/:bookingId" element={<BookingDetail />} />
        <Route path="/customer/complaints" element={<MyComplaints />} />
        <Route path="/customer/refunds" element={<MyRefunds />} />
      </Route>

      {/* Owner Routes */}
      <Route
        element={
          <ProtectedRoute allowedRole="OWNER">
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/owner" element={<OwnerDashboard />} />
        <Route path="/owner/trips" element={<OwnerTrips />} />
        <Route path="/owner/bookings" element={<OwnerBookings />} />
        <Route path="/owner/complaints" element={<OwnerComplaints />} />
        <Route path="/owner/approvals" element={<OwnerApprovals />} />
        <Route path="/owner/audit" element={<OwnerAuditLogs />} />
      </Route>

      {/* Root Redirect */}
      <Route
        path="/"
        element={
          isLoading ? (
            <div className="min-h-screen flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
            </div>
          ) : (
            <Navigate to={user?.role === 'OWNER' ? '/owner' : '/customer'} replace />
          )
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
