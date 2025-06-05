// WebSocket adapter that works with both simple WebSocket and Socket.IO backends
import { io, Socket } from 'socket.io-client'

export class WebSocketAdapter {
  private socket: Socket | null = null
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  constructor() {
    if (typeof window !== 'undefined') {
      this.connect()
    }
  }
  
  private connect() {
    try {
      // Import config dynamically to avoid SSR issues
      const { getConfig } = require('./config')
      const { websocketUrl } = getConfig()
      
      // For production, use the actual backend URL
      const baseUrl = websocketUrl.replace('wss://', 'https://').replace('ws://', 'http://')
      
      console.log('Connecting to backend via Socket.IO:', baseUrl)
      
      // Connect using Socket.IO which the backend supports
      this.socket = io(baseUrl, {
        path: '/ws/socket.io/',
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 20000
      })
      
      this.setupEventHandlers()
    } catch (error) {
      console.error('Failed to setup WebSocket:', error)
      this.emit('connection:failed', { error: 'Setup error' })
    }
  }
  
  private setupEventHandlers() {
    if (!this.socket) return
    
    this.socket.on('connect', () => {
      console.log('Socket.IO connected')
      this.reconnectAttempts = 0
      this.emit('connection:established', { connected: true })
    })
    
    this.socket.on('disconnect', (reason) => {
      console.log('Socket.IO disconnected:', reason)
      this.emit('connection:lost', { reason })
    })
    
    this.socket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error)
      this.emit('connection:error', { error: error.message })
    })
    
    // Map Socket.IO events to our expected events
    this.socket.on('system:state', (data) => {
      this.emit('system:state', data)
    })
    
    this.socket.on('agent:update', (data) => {
      this.emit('agent:update', data)
      this.emit('agent:thought', data)
      this.emit('agent:status', data)
    })
    
    this.socket.on('analysis:started', (data) => {
      this.emit('analysis:started', data)
    })
    
    this.socket.on('analysis:progress', (data) => {
      this.emit('analysis:progress', data)
    })
    
    this.socket.on('analysis:completed', (data) => {
      this.emit('analysis:completed', data)
    })
    
    this.socket.on('insight:generated', (data) => {
      this.emit('insight:generated', data)
    })
    
    this.socket.on('trend:update', (data) => {
      this.emit('trend:update', data)
    })
    
    // Handle all other events
    this.socket.onAny((event, data) => {
      console.log('Socket.IO event:', event, data)
      this.emit(event, data)
    })
  }
  
  public on(event: string, handler: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(handler)
    
    return () => {
      const handlers = this.listeners.get(event)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.listeners.delete(event)
        }
      }
    }
  }
  
  private emit(event: string, data: any) {
    const handlers = this.listeners.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error)
        }
      })
    }
  }
  
  public send(data: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit('message', data)
    } else {
      console.warn('Socket not connected, cannot send:', data)
    }
  }
  
  public requestAnalysis(data: { topic: string, [key: string]: any }): string {
    const requestId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    if (this.socket && this.socket.connected) {
      this.socket.emit('request_analysis', {
        request_id: requestId,
        ...data
      })
    }
    return requestId
  }
  
  public disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }
  
  public isConnected(): boolean {
    return this.socket?.connected || false
  }
}

// Create singleton
const websocketAdapter = new WebSocketAdapter()

export default websocketAdapter