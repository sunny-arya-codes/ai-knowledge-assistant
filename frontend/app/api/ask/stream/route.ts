export const runtime = 'nodejs'

export async function POST(request: Request) {
  const body = await request.json()

  const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

  let upstream
  try {
    upstream = await fetch(`${backendUrl}/ask/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch (err) {
    return new Response(
      JSON.stringify({ detail: 'Backend is starting up or temporarily unreachable. Please wait a moment and try again.' }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }

  if (!upstream.ok) {
    const errText = await upstream.text()
    return new Response(errText, {
      status: upstream.status,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  if (!upstream.body) {
    return new Response(JSON.stringify({ detail: 'No response body from upstream' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const stream = new ReadableStream({
    async start(controller) {
      const reader = upstream.body!.getReader()
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          controller.enqueue(value)
        }
      } catch (err) {
        console.error('SSE proxy error:', err)
      } finally {
        controller.close()
      }
    },
  })

  return new Response(stream, {
    status: 200,
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  })
}
