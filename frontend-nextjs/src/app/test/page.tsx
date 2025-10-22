'use client'

import Link from 'next/link'

export default function SimpleTestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-center text-white">
        <h1 className="text-4xl font-bold mb-8">ORFEAS Studio - Next.js</h1>
        <p className="text-xl mb-8">WebSocket Connectivity Testing</p>

        <div className="space-y-4">
          <Link
            href="/diagnostics"
            className="block bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-medium transition-colors"
          >
            🔧 Run Full Diagnostics
          </Link>

          <p className="text-gray-300 text-sm">
            Test WebSocket connections, API endpoints, and backend communication
          </p>
        </div>
      </div>
    </div>
  )
}
