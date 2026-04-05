// hooks/useAskStream.ts
import { useCallback, useRef, useState } from 'react'

type Status = 'idle' | 'loading' | 'streaming' | 'done' | 'error'

interface StreamState {
  answer: string
  sources: string[]
  status: Status
  error: string | null
}

interface UseAskStreamReturn extends StreamState {
  ask: (question: string) => Promise<void>
  reset: () => void
}

const INITIAL_STATE: StreamState = {
  answer: '',
  sources: [],
  status: 'idle',
  error: null,
}

export function useAskStream(): UseAskStreamReturn {
  const [state, setState] = useState<StreamState>(INITIAL_STATE)
  const abortRef = useRef<AbortController | null>(null)

  const reset = useCallback(() => {
    abortRef.current?.abort()
    setState(INITIAL_STATE)
  }, [])

  const ask = useCallback(async (question: string) => {
    // पिछली request cancel करो अगर चल रही हो
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setState({ answer: '', sources: [], status: 'loading', error: null })

    try {
      const response = await fetch('/api/ask/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail ?? 'Request failed')
      }

      if (!response.body) throw new Error('No response body')

      setState(prev => ({ ...prev, status: 'streaming' }))

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // SSE chunks decode करो — multiple events एक read में आ सकते हैं
        const raw = decoder.decode(value, { stream: true })
        const lines = raw.split('\n\n').filter(Boolean)

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue

          try {
            const payload = JSON.parse(line.slice(6)) // "data: " = 6 chars

            if (payload.token) {
              setState(prev => ({ ...prev, answer: prev.answer + payload.token }))
            }

            if (payload.done) {
              setState(prev => ({
                ...prev,
                sources: payload.sources ?? [],
                status: 'done',
              }))
            }

            if (payload.error) {
              throw new Error(payload.error)
            }
          } catch (parseErr) {
            // JSON parse fail — line skip करो, stream continue करो
            console.warn('SSE parse error:', parseErr)
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') return // user ने cancel किया

      setState(prev => ({
        ...prev,
        status: 'error',
        error: (err as Error).message ?? 'Something went wrong',
      }))
    }
  }, [])

  return { ...state, ask, reset }
}