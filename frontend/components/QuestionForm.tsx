// components/QuestionForm.tsx
import { FormEvent, useState } from 'react'

interface Props {
  onSubmit: (question: string) => void
  onReset: () => void
  disabled: boolean
}

export function QuestionForm({ onSubmit, onReset, disabled }: Props) {
  const [question, setQuestion] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = question.trim()
    if (!trimmed) return
    onSubmit(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="question-form">
      <input
        id="question-input"
        type="text"
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="Ask a question about your documents..."
        disabled={disabled}
        className="question-input"
        autoComplete="off"
      />
      <button
        id="submit-btn"
        type="submit"
        disabled={disabled || !question.trim()}
        className="btn-submit"
      >
        {disabled ? 'Thinking…' : 'Ask'}
      </button>
      <button
        id="clear-btn"
        type="button"
        onClick={() => { onReset(); setQuestion(''); }}
        className="btn-clear"
      >
        Clear
      </button>
    </form>
  )
}