// components/ConnectionStatus.tsx
import { ConnectionStatus as StatusType } from '@/hooks/useHealthCheck'

export function ConnectionStatus({ status }: { status: StatusType }) {
  if (status === 'connected') {
    return (
      <div className="status-badge connected">
        <span className="dot pulse-green"></span>
        <span>Backend Ready</span>
      </div>
    )
  }

  if (status === 'offline') {
    return (
      <div className="status-badge offline">
        <span className="dot static-red"></span>
        <span>Backend Offline</span>
      </div>
    )
  }

  return (
    <div className="status-badge checking">
      <span className="dot pulse-yellow"></span>
      <span>Connecting...</span>
    </div>
  )
}
