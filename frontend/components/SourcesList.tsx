// components/SourcesList.tsx

interface Props {
  sources: string[]
  status: string
}

export function SourcesList({ sources, status }: Props) {
  if (status !== 'done' || sources.length === 0) return null

  return (
    <div className="sources-section">
      <p className="sources-label">
        <span aria-hidden="true">📄</span> Sources
      </p>
      <div className="sources-list">
        {sources.map(source => (
          <span key={source} className="source-badge">
            {source}
          </span>
        ))}
      </div>
    </div>
  )
}