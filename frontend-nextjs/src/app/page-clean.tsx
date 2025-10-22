'use client'

import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-white">
                ORFEAS Studio
              </div>
              <div className="text-sm text-purple-300">
                Next.js Edition
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                href="/diagnostics"
                className="bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-300 px-3 py-1 rounded-lg text-sm font-medium transition-colors border border-yellow-500/30"
              >
                🔧 Diagnostics
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center text-white">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            ORFEAS Studio
          </h1>
          <h2 className="text-2xl font-semibold mb-6">
            AI-Powered 3D Model Generation
          </h2>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Transform your images into high-quality 3D models using advanced AI technology.
            Built with Next.js 15, React 19, and real-time WebSocket connectivity.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {/* Diagnostics Card */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-4xl mb-4">🔧</div>
              <h3 className="text-xl font-semibold mb-3">System Diagnostics</h3>
              <p className="text-gray-300 mb-4">
                Test WebSocket connections, API endpoints, and backend communication
              </p>
              <Link
                href="/diagnostics"
                className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-block"
              >
                Run Tests
              </Link>
            </div>

            {/* Features Card */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-3">Real-time Processing</h3>
              <p className="text-gray-300 mb-4">
                Watch your 3D models generate in real-time with live progress updates
              </p>
              <button
                disabled
                className="bg-gray-600 text-gray-300 px-4 py-2 rounded-lg font-medium inline-block cursor-not-allowed"
              >
                Coming Soon
              </button>
            </div>

            {/* Technology Card */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="text-xl font-semibold mb-3">Modern Stack</h3>
              <p className="text-gray-300 mb-4">
                Built with cutting-edge technology for optimal performance
              </p>
              <Link
                href="/test"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-block"
              >
                Test Page
              </Link>
            </div>
          </div>

          {/* Status Section */}
          <div className="mt-16 bg-black/20 backdrop-blur-lg rounded-xl p-8 border border-white/10">
            <h3 className="text-2xl font-semibold mb-6">System Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div>
                <h4 className="font-semibold text-purple-300 mb-2">Frontend</h4>
                <div className="space-y-1 text-sm">
                  <div>✅ Next.js 15 with App Router</div>
                  <div>✅ React 19 with TypeScript</div>
                  <div>✅ Tailwind CSS 4</div>
                  <div>✅ Socket.IO Client</div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-purple-300 mb-2">Backend</h4>
                <div className="space-y-1 text-sm">
                  <div>⏳ Python Flask Server</div>
                  <div>⏳ Socket.IO Server</div>
                  <div>⏳ AI Model Integration</div>
                  <div>⏳ 3D Generation Pipeline</div>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
              <p className="text-blue-300 text-sm">
                💡 <strong>Next Step:</strong> Run diagnostics to test all system components and WebSocket connectivity.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
