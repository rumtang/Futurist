import { io, Socket } from 'socket.io-client'

export interface AgentUpdate {
  agent: string
  event: string
  data: any
  timestamp: string
}

export interface SystemState {
  agents: Record<string, {
    status: string
    last_active: string | null
  }>
  system: {
    status: string
    version: string
    capabilities: string[]
  }
}

class SocketClient {
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
    // Extract base URL from websocket URL (convert wss:// to https://)
    const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8001'
    const baseUrl = wsUrl.replace('wss://', 'https://').replace('ws://', 'http://')
    
    this.socket = io(baseUrl, {
      path: '/ws/socket.io/',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
    })
    
    this.setupEventHandlers()
  }
  
  private setupEventHandlers() {
    if (!this.socket) return
    
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server')
      this.reconnectAttempts = 0
      this.emit('connection:established', { connected: true })
      
      // Subscribe to all updates by default
      this.subscribe('all')
    })
    
    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason)
      this.emit('connection:lost', { reason })
    })
    
    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.emit('connection:failed', { 
          error: 'Max reconnection attempts reached',
          attempts: this.reconnectAttempts 
        })
      }
    })
    
    // System events
    this.socket.on('system:state', (data: SystemState) => {
      this.emit('system:state', data)
    })
    
    // Agent events
    this.socket.on('agent:update', (data: AgentUpdate) => {
      this.emit('agent:update', data)
    })
    
    this.socket.on('agent:thinking', (data: any) => {
      this.emit('agent:thinking', data)
    })
    
    this.socket.on('agent:thought', (data: any) => {
      this.emit('agent:thought', data)
    })
    
    this.socket.on('agent:status', (data: any) => {
      this.emit('agent:status', data)
    })
    
    this.socket.on('agent:collaboration', (data: any) => {
      this.emit('agent:collaboration', data)
    })
    
    // Insight events
    this.socket.on('insight:generated', (data: any) => {
      this.emit('insight:generated', data)
    })
    
    // Graph events
    this.socket.on('graph:update', (data: any) => {
      this.emit('graph:update', data)
    })
    
    // Trend events
    this.socket.on('trend:update', (data: any) => {
      this.emit('trend:update', data)
    })
    
    // Scenario events
    this.socket.on('scenario:update', (data: any) => {
      this.emit('scenario:update', data)
    })
    
    // Analysis events
    this.socket.on('analysis:started', (data: any) => {
      this.emit('analysis:started', data)
    })
    
    this.socket.on('analysis:progress', (data: any) => {
      this.emit('analysis:progress', data)
    })
    
    this.socket.on('analysis:completed', (data: any) => {
      this.emit('analysis:completed', data)
    })
    
    // Subscription confirmation
    this.socket.on('subscription:confirmed', (data: any) => {
      this.emit('subscription:confirmed', data)
    })
  }
  
  public on(event: string, handler: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(handler)
    
    // Return unsubscribe function
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
  
  public off(event: string, handler?: (data: any) => void) {
    if (!handler) {
      this.listeners.delete(event)
    } else {
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
  
  public subscribe(type: string) {
    if (this.socket && this.socket.connected) {
      this.socket.emit('subscribe', { type })
    }
  }
  
  public unsubscribe(type: string) {
    if (this.socket && this.socket.connected) {
      this.socket.emit('unsubscribe', { type })
    }
  }
  
  public requestAnalysis(data: {
    topic: string
    depth?: string
    timeframe?: string
    focus_areas?: string[]
  }) {
    if (this.socket && this.socket.connected) {
      const requestId = `analysis_${Date.now()}`
      this.socket.emit('request_analysis', {
        id: requestId,
        ...data
      })
      return requestId
    }
    throw new Error('Socket not connected')
  }
  
  public ping() {
    if (this.socket && this.socket.connected) {
      this.socket.emit('ping')
    }
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
  
  public getSocket(): Socket | null {
    return this.socket
  }
}

// Create singleton instance
const socketClient = new SocketClient()

// Export singleton
export default socketClient

// Export types
export type { SocketClient }