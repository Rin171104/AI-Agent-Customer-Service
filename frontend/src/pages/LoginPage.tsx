import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../services/auth'
import { Bot, Mail, Lock, ArrowRight, Sparkles } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(email, password)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Đăng nhập thất bại')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-700 via-primary-600 to-accent-600 p-12 flex-col justify-between relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-72 h-72 bg-white rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent-400 rounded-full blur-3xl translate-x-1/2 translate-y-1/2" />
        </div>

        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Bot className="text-white" size={28} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Hiền Hựu Bus</h1>
              <p className="text-white/80">AI-Powered Customer Service</p>
            </div>
          </div>
        </div>

        <div className="relative z-10 space-y-8">
          <div className="space-y-4">
            <h2 className="text-4xl font-bold text-white leading-tight">
              Hệ thống hỗ trợ<br />
              <span className="text-accent-300">thông minh</span> cho<br />
              vận tải hành khách
            </h2>
            <p className="text-white/80 text-lg max-w-md">
              Quản lý chuyến xe, đặt vé, khiếu nại và hoàn tiền một cách hiệu quả với sự hỗ trợ của AI.
            </p>
          </div>

          {/* Feature highlights */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center mb-3">
                <Sparkles className="text-white" size={20} />
              </div>
              <h3 className="font-semibold text-white">AI Assistant</h3>
              <p className="text-sm text-white/70 mt-1">Hỗ trợ 24/7</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center mb-3">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white">Bảo mật</h3>
              <p className="text-sm text-white/70 mt-1">Dữ liệu an toàn</p>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-white/60 text-sm">
          © 2024 Hiền Hựu Bus. All rights reserved.
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-neutral-50">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center">
              <Bot className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">Hiền Hựu Bus</h1>
              <p className="text-sm text-neutral-500">AI-Powered</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-card p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-neutral-900">Đăng nhập</h2>
              <p className="text-neutral-500 mt-2">Chào mừng bạn quay trở lại</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <label className="block text-sm font-medium text-neutral-700">Email</label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400">
                    <Mail size={18} />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="input pl-11"
                    placeholder="email@example.com"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-neutral-700">Mật khẩu</label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400">
                    <Lock size={18} />
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input pl-11"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full py-3 text-base"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Đang đăng nhập...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Đăng nhập
                    <ArrowRight size={18} />
                  </span>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-neutral-500">
                Chưa có tài khoản?{' '}
                <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
                  Đăng ký
                </Link>
              </p>
            </div>
          </div>

          {/* Demo accounts */}
          <div className="mt-6 bg-white rounded-xl border border-neutral-200 p-4">
            <p className="text-sm font-medium text-neutral-700 mb-3 text-center">Tài khoản demo</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => {
                  setEmail('owner@hienhuu.vn')
                  setPassword('Owner@123')
                }}
                className="text-left p-3 rounded-lg bg-neutral-50 hover:bg-neutral-100 transition-colors"
              >
                <p className="font-medium text-neutral-900 text-sm">Owner</p>
                <p className="text-xs text-neutral-500 mt-0.5">owner@hienhuu.vn</p>
                <p className="text-xs text-neutral-400">Owner@123</p>
              </button>
              <button
                onClick={() => {
                  setEmail('customer@example.com')
                  setPassword('Customer@123')
                }}
                className="text-left p-3 rounded-lg bg-neutral-50 hover:bg-neutral-100 transition-colors"
              >
                <p className="font-medium text-neutral-900 text-sm">Customer</p>
                <p className="text-xs text-neutral-500 mt-0.5">customer@example.com</p>
                <p className="text-xs text-neutral-400">Customer@123</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
