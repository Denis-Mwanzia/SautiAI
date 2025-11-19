import { useState, useRef, useEffect } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { Send, Bot, User, Loader2 } from 'lucide-react'

export default function Chat() {
  const toast = useToast()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm Sauti AI, your civic intelligence assistant. I can help you understand citizen feedback data, analyze trends, and answer questions about sentiment, sectors, and issues. How can I help you today?",
      timestamp: new Date().toISOString()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, newUserMessage])

    try {
      const conversationHistory = messages
        .filter(msg => msg.role !== 'system')
        .map(msg => ({
          user: msg.role === 'user' ? msg.content : '',
          assistant: msg.role === 'assistant' ? msg.content : ''
        }))
        .filter(msg => msg.user || msg.assistant)

      const response = await api.post('/chat/message', {
        message: userMessage,
        conversation_history: conversationHistory
      })

      const assistantMessage = {
        role: 'assistant',
        content: response?.data?.data?.response || "I'm sorry, I couldn't process your request.",
        timestamp: response?.data?.data?.timestamp || new Date().toISOString(),
        intent: response?.data?.data?.intent,
        entities: response?.data?.data?.entities,
        dataPoints: response?.data?.data?.data_points,
        followUps: response?.data?.data?.follow_ups || []
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      let errorMsg = "I'm sorry, I encountered an error processing your request. Please try again."
      if (error.response?.status === 404) {
        errorMsg = "Chat features are currently disabled. Please enable AI features in the backend configuration."
      } else {
        errorMsg = error.response?.data?.detail || errorMsg
        toast.error(errorMsg)
      }
      const errorMessage = {
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date().toISOString(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Chat</h1>
        <p className="text-gray-600 text-sm">Ask questions about citizen feedback data and insights</p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 glass-card p-6 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[75%] rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-50 text-gray-900 border border-gray-200'
                } ${message.error ? 'border-2 border-red-300 bg-red-50' : ''}`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                {message.followUps && message.followUps.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Suggested follow-ups:</p>
                    <div className="flex flex-wrap gap-2">
                      {message.followUps.map((followUp, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            setInput(followUp)
                            inputRef.current?.focus()
                          }}
                          className="text-xs px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-all text-gray-700"
                        >
                          {followUp}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {message.dataPoints && typeof message.dataPoints === 'object' && Object.keys(message.dataPoints).length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-600">
                    <p className="font-semibold">Data Context:</p>
                    <p className="truncate">{JSON.stringify(message.dataPoints)}</p>
                  </div>
                )}
                <p className="text-xs mt-2 opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSend} className="border-t border-gray-200 pt-4">
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about sentiment, sectors, trends, or any feedback data..."
              className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
            >
              <Send className="h-4 w-4" />
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Try: "What's the sentiment distribution?", "Show me top issues", "How many feedback items do we have?"
          </p>
        </form>
      </div>
    </div>
  )
}
