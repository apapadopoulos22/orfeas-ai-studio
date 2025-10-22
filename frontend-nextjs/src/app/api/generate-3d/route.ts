import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000'

export async function POST(request: NextRequest) {
  try {
    // Get JSON data from the request
    const body = await request.json()

    // Forward the request to the Python backend
    const response = await fetch(`${BACKEND_URL}/api/generate-3d`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${error}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Generate 3D API error:', error)
    return NextResponse.json(
      { error: 'Failed to generate 3D model' },
      { status: 500 }
    )
  }
}
