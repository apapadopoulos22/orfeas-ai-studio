import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Test backend connection
    const response = await fetch('http://localhost:5000/api/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      const data = await response.json()
      return NextResponse.json({
        status: 'healthy',
        backend: 'connected',
        backendResponse: data,
        timestamp: new Date().toISOString()
      })
    } else {
      return NextResponse.json({
        status: 'backend_error',
        backend: 'disconnected',
        error: `Backend responded with ${response.status}`,
        timestamp: new Date().toISOString()
      }, { status: 503 })
    }
  } catch (error) {
    return NextResponse.json({
      status: 'backend_unreachable',
      backend: 'disconnected',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 503 })
  }
}
