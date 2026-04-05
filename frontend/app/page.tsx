'use client'

import { AnswerStream } from '@/components/AnswerStream'
import { QuestionForm } from '@/components/QuestionForm'
import { SourcesList } from '@/components/SourcesList'
import { ConnectionStatus } from '@/components/ConnectionStatus'
import { useAskStream } from '@/hooks/useAskStream'
import { useHealthCheck } from '@/hooks/useHealthCheck'

export default function Home() {
  const { answer, sources, status: askStatus, error, ask, reset } = useAskStream()
  const healthStatus = useHealthCheck()

  const isActive = askStatus === 'loading' || askStatus === 'streaming'
  const isOffline = healthStatus !== 'connected'

  return (
    <main className="app-container">
      <header className="header">
        <ConnectionStatus status={healthStatus} />
        <div className="header-icon" aria-hidden="true">✦</div>
        <h1 className="header-title">AI Knowledge Assistant</h1>
        <p className="header-subtitle">
          Ask questions about your uploaded documents and get AI&#8209;powered answers with source references.
        </p>
      </header>

      <QuestionForm 
        onSubmit={ask} 
        onReset={reset} 
        disabled={isActive || isOffline} 
        isOffline={isOffline} 
      />

      <div className="answer-section">
        <AnswerStream answer={answer} status={askStatus} error={error} />
        <SourcesList sources={sources} status={askStatus} />
      </div>
    </main>
  )
}