'use client'
import { useState, useRef, useEffect } from 'react'
import { HiChat, HiX, HiPaperAirplane } from 'react-icons/hi'
import { RiRobot2Line } from 'react-icons/ri'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatBot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hi! I'm Elias's virtual assistant. Ask me anything about his career, skills, or experience!" },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })),
        }),
      })

      if (!res.ok) {
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }
          return updated
        })
        setLoading(false)
        return
      }

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n').filter(l => l.startsWith('data: '))

          for (const line of lines) {
            try {
              const data = JSON.parse(line.slice(6))
              setMessages(prev => {
                const updated = [...prev]
                const last = updated[updated.length - 1]
                updated[updated.length - 1] = { role: 'assistant', content: last.content + data.content }
                return updated
              })
            } catch {
              // skip
            }
          }
        }
      }
    } catch {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }
        return updated
      })
    }
    setLoading(false)
  }

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 text-white flex items-center justify-center shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-110 transition-all duration-300 group"
      >
        {open ? <HiX className="w-6 h-6" /> : <HiChat className="w-6 h-6" />}
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 z-40 w-80 md:w-96 h-[500px] glass rounded-2xl border border-white/10 shadow-2xl shadow-black/50 flex flex-col overflow-hidden animate-slide-up">
          <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
              <RiRobot2Line className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-white">Virtual Assistant</h3>
              <p className="text-xs text-gray-500">Ask about Elias&apos;s career</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-tr-sm'
                      : 'bg-white/5 text-gray-300 rounded-tl-sm'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/5 rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="p-3 border-t border-white/5">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about my career..."
                className="flex-1 bg-white/5 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 border border-white/5 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="p-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white disabled:opacity-50 transition-all hover:shadow-lg hover:shadow-blue-500/25"
              >
                <HiPaperAirplane className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
