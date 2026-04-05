// app/api/health/route.ts
// Secure proxy for the backend health check endpoint to prevent ECONNREFUSED from crashing the frontend
export const runtime = 'nodejs'

export async function GET() {
  const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

  try {
    const res = await fetch(`${backendUrl}/health`, {
      // Small timeout to prevent the connection from hanging endlessly if backend is frozen
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
    // Expected to catch ECONNREFUSED or Timeout errors when starting up
    return new Response(JSON.stringify({ status: 'offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
