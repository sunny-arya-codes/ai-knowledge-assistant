// hooks/useHealthCheck.ts
import { useEffect, useState } from 'react'

export type ConnectionStatus = 'checking' | 'connected' | 'offline'

export function useHealthCheck() {
  const [status, setStatus] = useState<ConnectionStatus>('checking')

  useEffect(() => {
    let timeoutId: NodeJS.Timeout

    async function checkHealth() {
      try {
        const res = await fetch('/api/health')
        
        if (res.ok) {
           setStatus('connected')
           // Ping every 10s when healthy
           timeoutId = setTimeout(checkHealth, 10000)
        } else {
           setStatus('offline')
           // Ping every 2s when unhealthy/starting
           timeoutId = setTimeout(checkHealth, 2000)
        }
      } catch (err) {
        setStatus('offline')
        timeoutId = setTimeout(checkHealth, 2000)
      }
    }

    // Initial check
    checkHealth()

    return () => {
      clearTimeout(timeoutId)
    }
  }, [])

  return status
}
