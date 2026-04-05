// app/page.tsx
'use client'

import { AnswerStream } from '@/components/AnswerStream'
import { QuestionForm } from '@/components/QuestionForm'
import { SourcesList } from '@/components/SourcesList'
import { useAskStream } from '@/hooks/useAskStream'

export default function Home() {
  const { answer, sources, status, error, ask, reset } = useAskStream()

  const isActive = status === 'loading' || status === 'streaming'

  return (
    <main className="app-container">
      <header className="header">
        <div className="header-icon" aria-hidden="true">✦</div>
        <h1 className="header-title">AI Knowledge Assistant</h1>
        <p className="header-subtitle">
          Ask questions about your uploaded documents and get AI&#8209;powered answers with source references.
        </p>
      </header>

      <QuestionForm onSubmit={ask} onReset={reset} disabled={isActive} />

      <div className="answer-section">
        <AnswerStream answer={answer} status={status} error={error} />
        <SourcesList sources={sources} status={status} />
      </div>
    </main>
  )
}