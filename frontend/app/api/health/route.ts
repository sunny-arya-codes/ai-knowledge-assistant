export const runtime = 'nodejs'

export async function GET() {
  const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

  try {
    const res = await fetch(`${backendUrl}/health`, {
      signal: AbortSignal.timeout(3000)
    })

    if (res.ok) {
      return new Response(JSON.stringify({ status: 'ok' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    } else {
      return new Response(JSON.stringify({ status: 'offline' }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      })
    }
  } catch (err) {
    return new Response(JSON.stringify({ status: 'offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
