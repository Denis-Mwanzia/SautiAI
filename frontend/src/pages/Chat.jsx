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

    // Add user message
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, newUserMessage])

    try {
      // Build conversation history
      const conversationHistory = messages
        .filter(msg => msg.role !== 'system')
        .map(msg => ({
          user: msg.role === 'user' ? msg.content : '',
          assistant: msg.role === 'assistant' ? msg.content : ''
        }))
        .filter(msg => msg.user || msg.assistant)

      // Call chat API
      const response = await api.post('/chat/message', {
        message: userMessage,
        conversation_history: conversationHistory
      })

      // Add assistant response
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
      // Handle 404 gracefully (AI features disabled)
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
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      <div className="animate-slide-up mb-6">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
          Chat with Sauti AI
        </h1>
        <p className="text-gray-600 mt-2">Ask questions about citizen feedback data and insights</p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start gap-4 animate-slide-up ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center shadow-md">
                  <Bot className="h-6 w-6 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[75%] rounded-2xl p-4 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                    : 'bg-gray-100 text-gray-900'
                } ${message.error ? 'border-2 border-red-300' : ''}`}
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
                          className="text-xs px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-primary-400 transition-all text-gray-700 hover:text-primary-600"
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
                <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-gray-600" />
                </div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="flex items-start gap-4 animate-slide-up">
              <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center shadow-md">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div className="bg-gray-100 rounded-2xl p-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-primary-600" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSend} className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex items-center gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about sentiment, sectors, trends, or any feedback data..."
              className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-semibold flex items-center gap-2"
            >
              <Send className="h-5 w-5" />
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 ml-1">
            Try: "What's the sentiment distribution?", "Show me top issues", "How many feedback items do we have?"
          </p>
        </form>
      </div>
    </div>
  )
}

