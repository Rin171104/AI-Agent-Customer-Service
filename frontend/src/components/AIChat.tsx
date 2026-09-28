import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, AlertCircle, Sparkles, X, Minimize2 } from 'lucide-react'
import { cn } from '../lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isLoading?: boolean
  error?: string
}

interface AIChatProps {
  context?: 'customer' | 'owner'
  className?: string
  embedded?: boolean
  onClose?: () => void
}

// Mock AI responses based on context
const getAIResponse = async (message: string, context: 'customer' | 'owner'): Promise<string> => {
  await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 1000))

  const lowerMessage = message.toLowerCase()

  if (context === 'customer') {
    if (lowerMessage.includes('chuyến') || lowerMessage.includes('tuyến') || lowerMessage.includes('đi')) {
      return 'Tôi có thể giúp bạn tìm chuyến xe. Bạn muốn đi từ đâu đến đâu? Hãy vào mục "Tìm chuyến" để xem các tuyến xe hiện có.'
    }
    if (lowerMessage.includes('đặt') || lowerMessage.includes('vé') || lowerMessage.includes('book')) {
      return 'Để đặt vé, bạn cần chọn chuyến xe và số ghế muốn đặt. Sau khi đặt thành công, bạn sẽ cần thanh toán để xác nhận vé.'
    }
    if (lowerMessage.includes('thanh toán') || lowerMessage.includes('pay')) {
      return 'Bạn có thể thanh toán trực tiếp tại trang chi tiết booking. Hiện tại chúng tôi hỗ trợ thanh toán bằng chuyển khoản.'
    }
    if (lowerMessage.includes('hoàn tiền') || lowerMessage.includes('refund')) {
      return 'Nếu bạn cần hoàn tiền, vui lòng vào mục "Hoàn tiền" để tạo yêu cầu. Yêu cầu sẽ được gửi đến chủ nhà xe xét duyệt.'
    }
    if (lowerMessage.includes('khiếu nại') || lowerMessage.includes('complaint')) {
      return 'Bạn có thể tạo khiếu nại trong mục "Khiếu nại". Hãy mô tả chi tiết vấn đề của bạn và chúng tôi sẽ hỗ trợ giải quyết.'
    }
    return 'Cảm ơn bạn đã nhắn tin! Tôi có thể hỗ trợ bạn về: tìm chuyến xe, đặt vé, thanh toán, khiếu nại và hoàn tiền. Bạn cần giúp gì?'
  } else {
    if (lowerMessage.includes('hôm nay') || lowerMessage.includes('today')) {
      return 'Hôm nay bạn có thể xem tổng quan tình hình vận hành tại Dashboard. Tại đây hiển thị số chuyến xe, booking, doanh thu và các khiếu nại.'
    }
    if (lowerMessage.includes('booking') || lowerMessage.includes('đặt vé')) {
      return 'Bạn có thể xem danh sách đặt vé tại mục "Đặt vé". Tại đây hiển thị thông tin chi tiết từng booking và trạng thái thanh toán.'
    }
    if (lowerMessage.includes('hoàn tiền') || lowerMessage.includes('refund')) {
      return 'Để duyệt hoàn tiền, vào mục "Duyệt hoàn tiền". Bạn sẽ thấy danh sách các yêu cầu và có thể phê duyệt hoặc từ chối.'
    }
    if (lowerMessage.includes('khiếu nại') || lowerMessage.includes('complaint')) {
      return 'Mục "Khiếu nại" hiển thị các khiếu nại từ khách hàng. Bạn có thể tiếp nhận và giải quyết từng khiếu nại.'
    }
    if (lowerMessage.includes('doanh thu') || lowerMessage.includes('revenue')) {
      return 'Doanh thu được hiển thị tại Dashboard. Bạn có thể xem chi tiết từ các booking đã thanh toán thành công.'
    }
    return 'Xin chào! Tôi là AI Assistant của Hiền Hựu Bus. Tôi có thể hỗ trợ bạn quản lý chuyến xe, booking, khiếu nại và hoàn tiền. Bạn cần giúp gì?'
  }
}

export default function AIChat({ context = 'customer', className, embedded = false, onClose }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: context === 'customer'
        ? 'Xin chào! Tôi là AI Assistant của Hiền Hựu Bus. Tôi có thể hỗ trợ bạn:\n\n• Tìm chuyến xe\n• Đặt vé\n• Kiểm tra booking\n• Chính sách\n• Khiếu nại\n• Hoàn tiền\n\nBạn cần giúp gì?'
        : 'Xin chào! Tôi là AI Assistant của Hiền Hựu Bus dành cho chủ nhà xe. Tôi có thể hỗ trợ:\n\n• Tổng hợp tình hình vận hành\n• Tra cứu booking\n• Tra cứu khiếu nại\n• Duyệt hoàn tiền\n• Hỗ trợ chính sách\n\nBạn cần giúp gì?',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isMinimized, setIsMinimized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || messages.some((m) => m.isLoading)) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')

    // Add loading message
    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    }
    setMessages((prev) => [...prev, loadingMessage])

    try {
      const response = await getAIResponse(input.trim(), context)

      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingMessage.id
            ? { ...m, id: `ai-${Date.now()}`, content: response, isLoading: false }
            : m
        )
      )
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingMessage.id
            ? {
                ...m,
                id: `error-${Date.now()}`,
                content: 'Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu. Vui lòng thử lại.',
                isLoading: false,
                error: 'Failed to get response',
              }
            : m
        )
      )
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickActions = context === 'customer'
    ? [
        { label: 'Tìm chuyến', query: 'Tôi muốn tìm chuyến xe' },
        { label: 'Đặt vé', query: 'Hướng dẫn đặt vé' },
        { label: 'Hoàn tiền', query: 'Làm sao để yêu cầu hoàn tiền?' },
        { label: 'Khiếu nại', query: 'Tôi muốn tạo khiếu nại' },
      ]
    : [
        { label: 'Tổng quan', query: 'Hôm nay có bao nhiêu booking?' },
        { label: 'Hoàn tiền', query: 'Có refund nào đang chờ duyệt không?' },
        { label: 'Khiếu nại', query: 'Có khiếu nại nào mới không?' },
        { label: 'Doanh thu', query: 'Doanh thu hôm nay là bao nhiêu?' },
      ]

  if (isMinimized && !embedded) {
    return (
      <button
        onClick={() => setIsMinimized(false)}
        className={cn(
          'fixed bottom-6 right-6 w-14 h-14 rounded-full',
          'bg-gradient-to-br from-primary-600 to-accent-600',
          'text-white shadow-elevated',
          'flex items-center justify-center',
          'hover:scale-105 transition-transform duration-200',
          'z-50',
          className
        )}
      >
        <Sparkles size={24} />
      </button>
    )
  }

  return (
    <div
      className={cn(
        'bg-white rounded-2xl shadow-elevated overflow-hidden',
        embedded ? 'h-full' : 'fixed bottom-6 right-6 w-96 h-[32rem] flex flex-col z-50',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-neutral-100 bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <Sparkles className="text-white" size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-white">Hiền Hựu AI</h3>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-white/80">Online</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {!embedded && (
            <button
              onClick={() => setIsMinimized(true)}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <Minimize2 size={18} />
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn('flex', message.role === 'user' ? 'justify-end' : 'justify-start')}
          >
            <div className="flex gap-2 max-w-[85%]">
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0">
                  <Bot className="text-white" size={16} />
                </div>
              )}
              <div>
                {message.isLoading ? (
                  <div className="chat-bubble chat-bubble-ai flex items-center gap-2">
                    <Loader2 className="animate-spin" size={16} />
                    <span className="text-neutral-500">Đang xử lý...</span>
                  </div>
                ) : message.error ? (
                  <div className="chat-bubble chat-bubble-ai flex items-start gap-2 bg-red-50 border-red-200">
                    <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={16} />
                    <span>{message.content}</span>
                  </div>
                ) : (
                  <div className={cn('chat-bubble', message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai')}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                )}
              </div>
              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-neutral-200 flex items-center justify-center flex-shrink-0">
                  <User className="text-neutral-600" size={16} />
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action) => (
              <button
                key={action.label}
                onClick={() => {
                  setInput(action.query)
                  inputRef.current?.focus()
                }}
                className="px-3 py-1.5 text-xs font-medium bg-neutral-100 text-neutral-700 rounded-full hover:bg-neutral-200 transition-colors"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-neutral-100">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi..."
            rows={1}
            className="flex-1 px-4 py-2.5 bg-neutral-50 border border-neutral-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-sm"
            style={{ maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || messages.some((m) => m.isLoading)}
            className="p-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-xs text-neutral-400 mt-2 text-center">
          Powered by Hiền Hựu AI • {context === 'customer' ? 'Hỗ trợ khách hàng' : 'Hỗ trợ vận hành'}
        </p>
      </div>
    </div>
  )
}
