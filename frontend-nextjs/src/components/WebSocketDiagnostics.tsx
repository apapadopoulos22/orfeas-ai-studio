'use client'

import { useSocket } from '@/hooks/useSocket'
import { Activity, CheckCircle, Clock, Wifi, WifiOff, XCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

interface DiagnosticResult {
  test: string
  status: 'pending' | 'success' | 'error'
  message: string
  timestamp: string
}

export default function WebSocketDiagnostics() {
  const { socket, connected, connectionError } = useSocket('http://localhost:5000')
  const [diagnostics, setDiagnostics] = useState<DiagnosticResult[]>([])
  const [isRunning, setIsRunning] = useState(false)

  const addDiagnostic = (test: string, status: 'pending' | 'success' | 'error', message: string) => {
    setDiagnostics(prev => [...prev, {
      test,
      status,
      message,
      timestamp: new Date().toLocaleTimeString()
    }])
  }

  const runDiagnostics = async () => {
    setIsRunning(true)
    setDiagnostics([])

    // Test 1: Backend Connection
    addDiagnostic('Backend Health Check', 'pending', 'Testing backend server...')

    try {
      const response = await fetch('/api/health')
      if (response.ok) {
        const data = await response.json()
        addDiagnostic('Backend Health Check', 'success', `Backend responding: ${data.status}`)
      } else {
        addDiagnostic('Backend Health Check', 'error', `HTTP ${response.status}`)
      }
    } catch (error) {
      addDiagnostic('Backend Health Check', 'error', `Connection failed: ${error}`)
    }

    // Test 2: Direct Backend Connection
    try {
      const response = await fetch('http://localhost:5000/api/health')
      if (response.ok) {
        const data = await response.json()
        addDiagnostic('Direct Backend Connection', 'success', `Direct connection OK: ${data.server}`)
      } else {
        addDiagnostic('Direct Backend Connection', 'error', `HTTP ${response.status}`)
      }
    } catch (error) {
      addDiagnostic('Direct Backend Connection', 'error', `Direct connection failed: ${error}`)
    }

    // Test 3: WebSocket Connection Status
    if (connected) {
      addDiagnostic('WebSocket Connection', 'success', `Connected with transport: ${socket?.io?.engine?.transport?.name || 'unknown'}`)
    } else {
      addDiagnostic('WebSocket Connection', 'error', connectionError || 'Not connected')
    }

    // Test 4: Socket Event Handling
    if (socket && connected) {
      try {
        // Test custom event emission
        socket.emit('test_ping', { timestamp: Date.now() })

        socket.on('test_pong', (data) => {
          addDiagnostic('Socket Event Test', 'success', `Ping-pong successful: ${JSON.stringify(data)}`)
        })

        // Timeout for ping test
        setTimeout(() => {
          socket.off('test_pong')
          addDiagnostic('Socket Event Test', 'error', 'No pong response received (timeout)')
        }, 3000)

      } catch (error) {
        addDiagnostic('Socket Event Test', 'error', `Event test failed: ${error}`)
      }
    } else {
      addDiagnostic('Socket Event Test', 'error', 'Cannot test events - no socket connection')
    }

    // Test 5: File Upload API
    try {
      const testBlob = new Blob(['test'], { type: 'text/plain' })
      const formData = new FormData()
      formData.append('image', testBlob, 'test.txt')

      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        addDiagnostic('Upload API Test', 'success', `Upload API working: ${data.message || 'OK'}`)
      } else {
        const error = await response.text()
        addDiagnostic('Upload API Test', 'error', `Upload failed: ${error}`)
      }
    } catch (error) {
      addDiagnostic('Upload API Test', 'error', `Upload API error: ${error}`)
    }

    setIsRunning(false)
  }

  useEffect(() => {
    if (socket) {
      socket.on('connect', () => {
        console.log('✅ Socket connected in diagnostics')
      })

      socket.on('disconnect', () => {
        console.log('❌ Socket disconnected in diagnostics')
      })

      socket.on('connect_error', (error) => {
        console.error('❌ Socket connection error in diagnostics:', error)
      })
    }

    return () => {
      if (socket) {
        socket.off('connect')
        socket.off('disconnect')
        socket.off('connect_error')
      }
    }
  }, [socket])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />
      case 'pending': return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />
      default: return <Activity className="w-5 h-5 text-gray-500" />
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">WebSocket Diagnostics</h1>
              <p className="text-gray-600 mt-1">Test ORFEAS Frontend ↔ Backend Communication</p>
            </div>

            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                connected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {connected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
                <span>{connected ? 'Connected' : 'Disconnected'}</span>
              </div>

              <button
                onClick={runDiagnostics}
                disabled={isRunning}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {isRunning ? 'Running Tests...' : 'Run Diagnostics'}
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          {/* Connection Status */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h2 className="text-lg font-semibold mb-3">Current Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">WebSocket Status:</span>
                <span className={`ml-2 ${connected ? 'text-green-600' : 'text-red-600'}`}>
                  {connected ? '✅ Connected' : '❌ Disconnected'}
                </span>
              </div>
              <div>
                <span className="font-medium">Backend URL:</span>
                <span className="ml-2 text-gray-600">http://localhost:5000</span>
              </div>
              <div>
                <span className="font-medium">Transport:</span>
                <span className="ml-2 text-gray-600">
                  {socket?.io?.engine?.transport?.name || 'Not connected'}
                </span>
              </div>
              <div>
                <span className="font-medium">Socket ID:</span>
                <span className="ml-2 text-gray-600 font-mono text-xs">
                  {socket?.id || 'None'}
                </span>
              </div>
              {connectionError && (
                <div className="md:col-span-2">
                  <span className="font-medium">Error:</span>
                  <span className="ml-2 text-red-600">{connectionError}</span>
                </div>
              )}
            </div>
          </div>

          {/* Diagnostic Results */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Diagnostic Results</h2>

            {diagnostics.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                Click &quot;Run Diagnostics&quot; to test all connections
              </div>
            ) : (
              <div className="space-y-3">
                {diagnostics.map((result, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-4 rounded-lg border ${
                      result.status === 'success'
                        ? 'bg-green-50 border-green-200'
                        : result.status === 'error'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-yellow-50 border-yellow-200'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(result.status)}
                      <div>
                        <div className="font-medium text-gray-900">{result.test}</div>
                        <div className="text-sm text-gray-600">{result.message}</div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">{result.timestamp}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Quick Fixes</h3>
            <div className="text-sm text-blue-800 space-y-1">
              <div>• Ensure backend server is running on port 5000</div>
              <div>• Check if firewall is blocking connections</div>
              <div>• Verify Socket.IO client version compatibility</div>
              <div>• Clear browser cache and reload page</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
