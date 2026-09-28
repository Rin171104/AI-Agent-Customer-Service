import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('vi-VN').format(amount) + ' VND'
}

export function formatCurrencyShort(amount: number): string {
  if (amount >= 1000000) {
    return (amount / 1000000).toFixed(1) + 'M'
  }
  if (amount >= 1000) {
    return (amount / 1000).toFixed(0) + 'K'
  }
  return amount.toString()
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export function formatDateTime(date: string): string {
  return new Date(date).toLocaleString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatTime(date: string): string {
  return new Date(date).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    PENDING_PAYMENT: 'bg-amber-50 text-amber-700 border-amber-200',
    CONFIRMED: 'bg-green-50 text-green-700 border-green-200',
    CANCELLED: 'bg-red-50 text-red-700 border-red-200',
    PAID: 'bg-green-50 text-green-700 border-green-200',
    PENDING: 'bg-amber-50 text-amber-700 border-amber-200',
    FAILED: 'bg-red-50 text-red-700 border-red-200',
    OPEN: 'bg-blue-50 text-blue-700 border-blue-200',
    IN_PROGRESS: 'bg-orange-50 text-orange-700 border-orange-200',
    RESOLVED: 'bg-green-50 text-green-700 border-green-200',
    WAITING_OWNER_APPROVAL: 'bg-amber-50 text-amber-700 border-amber-200',
    APPROVED: 'bg-green-50 text-green-700 border-green-200',
    REJECTED: 'bg-red-50 text-red-700 border-red-200',
    REFUNDED: 'bg-purple-50 text-purple-700 border-purple-200',
    ACTIVE: 'bg-green-50 text-green-700 border-green-200',
    REQUESTED: 'bg-blue-50 text-blue-700 border-blue-200',
  }
  return colors[status] || 'bg-neutral-100 text-neutral-700 border-neutral-200'
}

export function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    PENDING_PAYMENT: 'Chờ thanh toán',
    CONFIRMED: 'Đã xác nhận',
    CANCELLED: 'Đã hủy',
    PAID: 'Đã thanh toán',
    PENDING: 'Đang chờ',
    FAILED: 'Thất bại',
    OPEN: 'Mở',
    IN_PROGRESS: 'Đang xử lý',
    RESOLVED: 'Đã giải quyết',
    WAITING_OWNER_APPROVAL: 'Chờ duyệt',
    APPROVED: 'Đã duyệt',
    REJECTED: 'Từ chối',
    REFUNDED: 'Đã hoàn tiền',
    ACTIVE: 'Hoạt động',
    REQUESTED: 'Đã gửi',
  }
  return texts[status] || status
}
