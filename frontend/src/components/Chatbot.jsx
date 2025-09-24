import { useEffect, useRef, useState } from 'react'
import api from '../lib/api'
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000'

const STARTER_SUGGESTIONS = [
  'Plan a 20-minute dinner under 600 calories',
  'Swap dairy for lactose-free options in mac and cheese',
  'High-protein lunch with chicken and quinoa',
]

export default function Chatbot({ sessionId, selectedRecipe, healthProfile }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const endRef = useRef(null)
  const streamingRef = useRef(false)
  const [streaming, setStreaming] = useState(false)
  const inputRef = useRef(null)
  const scrollRef = useRef(null)
  const [showScrollBtn, setShowScrollBtn] = useState(false)
  const currentEsRef = useRef(null)
  const finishStreamRef = useRef(null)

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/api/chat/history', { params: { session_id: sessionId } })
        setMessages(res.data || [])
      } catch {
        setError('Failed to load chat history.')
      }
    }
    if (sessionId) load()
  }, [sessionId])

  useEffect(() => {
    // Keep the newest message in view, especially during streaming
    endRef.current?.scrollIntoView({ behavior: streamingRef.current ? 'auto' : 'smooth' })
  }, [messages])

  // Track scroll position to toggle scroll-to-bottom button
  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const onScroll = () => {
      const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80
      setShowScrollBtn(!nearBottom)
    }
    el.addEventListener('scroll', onScroll)
    onScroll()
    return () => el.removeEventListener('scroll', onScroll)
  }, [])

  const onSend = async (preset) => {
    const text = (preset ?? input).trim()
    if (!text) return
    setInput('')
    setError('')

    // Prevent duplicate messages by checking the last message
    const lastMessage = messages[messages.length - 1]
    if (lastMessage?.content === text) {
      return
    }

    const optimistic = [...messages, { role: 'user', content: text }]
    setMessages(optimistic)
    setSending(true)

    try {
      const context = {
        ...(healthProfile || {}),
        ...(selectedRecipe ? { selectedRecipe: { title: selectedRecipe.title, summary: selectedRecipe.summary } } : {}),
      }
      // Try SSE streaming first
      const params = new URLSearchParams({
        session_id: sessionId,
        message: text,
        use_graph: 'true',
        context: JSON.stringify(context),
      })

      let closed = false
      await new Promise((resolve, reject) => {
        try {
          const es = new EventSource(`${BASE}/api/chat/stream?${params.toString()}`)
          currentEsRef.current = es

          // Start an empty assistant message we will grow progressively
          setMessages((prev) => [...prev, { role: 'assistant', content: '' }])
          streamingRef.current = true
          setStreaming(true)

          // Allow external cancellation (Stop button)
          finishStreamRef.current = () => {
            if (!closed) {
              es.close()
              closed = true
              streamingRef.current = false
              setStreaming(false)
              resolve()
            }
          }

          es.addEventListener('message', (ev) => {
            const chunk = ev.data || ''
            if (chunk.startsWith('ERROR:')) {
              setError(chunk.replace(/^ERROR:\s*/, ''))
              es.close()
              closed = true
              reject(new Error(chunk))
              return
            }
            setMessages((prev) => {
              const next = [...prev]
              const last = next[next.length - 1]
              if (last && last.role === 'assistant') {
                last.content = (last.content || '') + chunk
              } else {
                next.push({ role: 'assistant', content: chunk })
              }
              return next
            })
          })

          es.addEventListener('end', () => {
            es.close()
            closed = true
            streamingRef.current = false
            setStreaming(false)
            currentEsRef.current = null
            finishStreamRef.current = null
            resolve()
          })

          es.onerror = (e) => {
            // Fallback to non-streaming if SSE fails early
            if (!closed) {
              es.close()
              streamingRef.current = false
              setStreaming(false)
              currentEsRef.current = null
              finishStreamRef.current = null
              reject(new Error('SSE failed'))
            }
          }
        } catch (err) {
          reject(err)
        }
      })
    } catch {
      // Fallback to non-streaming POST
      try {
        const context = {
          ...(healthProfile || {}),
          ...(selectedRecipe ? { selectedRecipe: { title: selectedRecipe.title, summary: selectedRecipe.summary } } : {}),
        }
        const res = await api.post('/api/chat', {
          session_id: sessionId,
          message: text,
          context,
          use_graph: true,
        })
        setMessages([...optimistic, { role: 'assistant', content: res.data.reply }])
      } catch {
        setError('Message failed. Please try again.')
        setMessages(optimistic)
      }
    } finally {
      setSending(false)
      // Refocus input for faster follow-ups
      inputRef.current?.focus()
    }
  }

  // Auto-expand textarea up to 6 lines
  const onInputChange = (e) => {
    const el = e.target
    setInput(el.value)
    requestAnimationFrame(() => {
      if (!el) return
      el.style.height = 'auto'
      const lineHeight = 20 // approximate px per line for text-sm/base
      const maxLines = 6
      const maxHeight = lineHeight * maxLines
      const newHeight = Math.min(maxHeight, el.scrollHeight)
      el.style.height = newHeight + 'px'
    })
  }

  const onStop = () => {
    // Cancel current stream if any
    finishStreamRef.current?.()
  }

  return (
    <div className="bg-white rounded-xl shadow flex flex-col h-[70vh] sm:h-[560px]">
      <div className="p-3 sm:p-4 border-b flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold">Chat Assistant</h2>
          {selectedRecipe && (
            <p className="text-xs text-gray-600 mt-1 line-clamp-2">
              Context: <span className="font-medium">{selectedRecipe.title}</span>
            </p>
          )}
        </div>
        {messages.length > 0 && (
          <button
            onClick={() => setMessages([])}
            className="text-sm text-gray-500 hover:text-gray-700"
            title="Clear chat"
          >
            Clear Chat
          </button>
        )}
      </div>

      <div ref={scrollRef} className="flex-1 overflow-auto p-2 sm:p-3 space-y-2 bg-gray-50 relative">
        {error && (
          <div role="alert" className="text-sm text-red-700 bg-red-50 border border-red-200 rounded px-3 py-2">
            {error}
          </div>
        )}

        {messages.length === 0 && !sending && (
          <div className="text-sm text-gray-600">
            <p className="mb-2">Try one:</p>
            <div className="flex flex-wrap gap-2">
              {STARTER_SUGGESTIONS.map((s) => (
                <button key={s} className="text-left border bg-white px-3 py-2 rounded hover:bg-gray-50" onClick={() => onSend(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>{
            m.role === 'user' ? (
              <div className="inline-block bg-indigo-600 text-white px-3 py-2 rounded-lg break-words whitespace-pre-line">
                {m.content}
              </div>
            ) : (
              <div 
                className="inline-block bg-white border px-3 py-2 rounded-lg break-words text-left max-w-full"
                style={{ whiteSpace: 'pre-line' }}
                dangerouslySetInnerHTML={{
                  __html: m.content
                    // Format headers
                    .replace(/^### (.*$)/gm, '<h3 class="font-bold text-lg mt-2">$1</h3>')
                    .replace(/^#### (.*$)/gm, '<h4 class="font-bold mt-3">$1</h4>')
                    // Format numbered lists
                    .replace(/^(\d+)\.\s+(.*$)/gm, '<div class="flex"><span class="mr-2">$1.</span><span>$2</span></div>')
                    // Format bullet points
                    .replace(/^•\s+(.*$)/gm, '<div class="flex"><span class="mr-2">•</span><span>$1</span></div>')
                    // Format bold text
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    // Format horizontal rules
                    .replace(/^-{3,}/g, '<hr class="my-3 border-t border-gray-200">')
                    // Convert newlines to <br> but prevent multiple consecutive ones
                    .replace(/\n{2,}/g, '\n').replace(/\n/g, '<br/>')
                }}
              />
            )}
          </div>
        ))}

        {sending && !streaming && (
          <div className="text-left">
            <span className="inline-block bg-white border px-3 py-2 rounded-lg text-gray-500">Assistant is typing…</span>
          </div>
        )}
        {streaming && (
          <div className="text-left">
            <div className="inline-block bg-white border px-3 py-2 rounded-lg w-5/6 max-w-[680px]">
              <div className="h-3 bg-gray-200 rounded w-5/6 mb-2 animate-pulse" />
              <div className="h-3 bg-gray-200 rounded w-4/6 mb-2 animate-pulse" />
              <div className="h-3 bg-gray-200 rounded w-3/6 animate-pulse" />
            </div>
          </div>
        )}
        <div ref={endRef} />

        {showScrollBtn && (
          <button
            onClick={() => endRef.current?.scrollIntoView({ behavior: 'smooth' })}
            className="absolute right-3 bottom-20 sm:bottom-24 bg-white border shadow px-3 py-1.5 rounded text-sm text-gray-700 hover:bg-gray-50"
            aria-label="Scroll to bottom"
          >
            ↓ Newest
          </button>
        )}
      </div>

      {/* Sticky input on mobile for better reachability */}
      <div className="p-2 sm:p-3 border-t sticky bottom-0 bg-white">
        <div className="flex gap-2 items-start">
          <textarea
            ref={inputRef}
            className="flex-1 border rounded px-3 py-3 text-sm sm:text-base resize-none max-h-40"
            rows={1}
            value={input}
            onChange={onInputChange}
            placeholder="Ask for substitutions, steps, or health-focused options…"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                onSend()
              }
            }}
            aria-label="Chat input"
          />
          <button
            onClick={() => onSend()}
            disabled={sending}
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2 rounded min-w-[72px]"
            aria-label="Send message"
          >
            {sending ? 'Sending…' : 'Send'}
          </button>
          {streaming && (
            <button
              onClick={onStop}
              className="bg-white border hover:bg-gray-50 text-gray-800 text-sm px-3 py-2 rounded"
              aria-label="Stop generating"
            >
              Stop
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
