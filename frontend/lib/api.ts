// lib/api.ts

export interface AskResponse {
  answer: string
  sources: string[]
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail ?? 'Failed to get answer')
  }

  return response.json()
}