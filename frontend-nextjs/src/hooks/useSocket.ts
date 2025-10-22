'use client'

import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'

interface UseSocketReturn {
  socket: Socket | null
  connected: boolean
  connectionError: string | null
}

export function useSocket(url: string): UseSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const socketRef = useRef<Socket | null>(null)
  const connectionAttempts = useRef(0)

  useEffect(() => {
    const connectSocket = () => {
      // Clear any existing socket
      if (socketRef.current) {
        socketRef.current.removeAllListeners()
        socketRef.current.disconnect()
      }

      // Reset connection error
      setConnectionError(null)

      console.log(`Attempting to connect to WebSocket: ${url}`)

      // Create socket connection with robust configuration
      const socketInstance = io(url, {
        transports: ['polling', 'websocket'], // Start with polling, upgrade to websocket
        upgrade: true,
        timeout: 10000,
        forceNew: true,
        reconnection: true,
        reconnectionAttempts: 10,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000
      })

      socketRef.current = socketInstance
      setSocket(socketInstance)

      // Connection success
      socketInstance.on('connect', () => {
        console.log('✅ Socket connected successfully:', socketInstance.id)
        console.log('Transport:', socketInstance.io.engine.transport.name)
        setConnected(true)
        setConnectionError(null)
        connectionAttempts.current = 0
      })

      // Connection failure
      socketInstance.on('disconnect', (reason) => {
        console.log('🔌 Socket disconnected:', reason)
        setConnected(false)

        if (reason === 'io server disconnect') {
          // Server initiated disconnect, try to reconnect
          socketInstance.connect()
        }
      })

      // Connection errors
      socketInstance.on('connect_error', (error) => {
        connectionAttempts.current += 1
        console.error(`❌ Socket connection error (attempt ${connectionAttempts.current}):`, error.message)
        setConnected(false)

        // Set user-friendly error message
        if (error.message.includes('ECONNREFUSED')) {
          setConnectionError('Backend server is not running on port 5000')
        } else if (error.message.includes('timeout')) {
          setConnectionError('Connection timeout - server may be overloaded')
        } else {
          setConnectionError(`Connection failed: ${error.message}`)
        }

        // After multiple failed attempts, wait longer before next attempt
        if (connectionAttempts.current >= 5) {
          console.log('⏳ Multiple connection failures, extending retry delay...')
        }
      })

      // Reconnection success
      socketInstance.on('reconnect', (attemptNumber) => {
        console.log(`🔄 Socket reconnected after ${attemptNumber} attempts`)
        setConnected(true)
        setConnectionError(null)
        connectionAttempts.current = 0
      })

      // Reconnection attempts
      socketInstance.on('reconnect_attempt', (attemptNumber) => {
        console.log(`🔄 Reconnection attempt ${attemptNumber}...`)
      })

      // Reconnection errors
      socketInstance.on('reconnect_error', (error) => {
        console.error('🔄 Reconnection error:', error.message)
      })

      // Transport upgrade
      socketInstance.on('upgrade', () => {
        console.log('⚡ Transport upgraded to:', socketInstance.io.engine.transport.name)
      })

      // Transport upgrade error
      socketInstance.on('upgrade_error', (error) => {
        console.log('⚡ Transport upgrade failed:', error.message, '- staying on polling')
      })
    }

    // Initial connection
    connectSocket()

    // Cleanup on unmount
    return () => {
      const currentSocket = socketRef.current

      if (currentSocket) {
        console.log('🧹 Cleaning up socket connection')
        currentSocket.removeAllListeners()
        currentSocket.disconnect()
      }

      socketRef.current = null
    }
  }, [url])

  return { socket, connected, connectionError }
}
