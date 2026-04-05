
interface Props {
  answer: string
  status: 'idle' | 'loading' | 'streaming' | 'done' | 'error'
  error: string | null
}

export function AnswerStream({ answer, status, error }: Props) {
  if (status === 'idle') return null

  if (status === 'loading') {
    return (
      <div className="glass-card loading-container">
        <div className="loading-label">
          <span className="loading-dot" />
          <span className="loading-dot" />
          <span className="loading-dot" />
          <span>Searching documents…</span>
        </div>
        <div className="skeleton-lines">
          <div className="skeleton-line" />
          <div className="skeleton-line" />
          <div className="skeleton-line" />
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="error-card">
        <span className="error-icon" aria-hidden="true">⚠</span>
        <span className="error-message">{error}</span>
      </div>
    )
  }

  return (
    <div className="answer-card">
      {answer}
      {status === 'streaming' && (
        <span className="streaming-cursor" aria-hidden="true" />
      )}
    </div>
  )
}