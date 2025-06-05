// Simple WebSocket implementation without Socket.io
export class SimpleWebSocket {
  private ws: WebSocket | null = null
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimeout: NodeJS.Timeout | null = null
  
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
    
    // Handle production URLs properly
    let wsUrl = websocketUrl
    
    // If we're in production and have an HTTPS URL, convert to WSS
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      wsUrl = wsUrl.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
    }
    
    // Ensure we have the correct protocol
    if (!wsUrl.startsWith('ws://') && !wsUrl.startsWith('wss://')) {
      wsUrl = window.location.protocol === 'https:' ? `wss://${wsUrl}` : `ws://${wsUrl}`
    }
    
    const fullUrl = `${wsUrl}/simple-ws`
    
    console.log('Connecting to WebSocket:', fullUrl)
    
    try {
      this.ws = new WebSocket(fullUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connection:established', { connected: true })
        
        // Send subscribe message
        this.send({ type: 'subscribe', channel: 'all' })
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('WebSocket message:', data)
          
          // Emit based on message type
          if (data.type) {
            this.emit(data.type, data)
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('connection:error', { error })
      }
      
      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        this.emit('connection:lost', { code: event.code, reason: event.reason })
        
        // Attempt reconnection
        this.scheduleReconnect()
      }
    } catch (e) {
      console.error('Failed to create WebSocket:', e)
      this.scheduleReconnect()
    }
    } catch (configError) {
      console.error('Failed to load config:', configError)
      // Don't attempt reconnection if config is broken
      this.emit('connection:failed', { error: 'Config error' })
    }
  }
  
  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      this.emit('connection:failed', { attempts: this.reconnectAttempts })
      return
    }
    
    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000)
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    this.reconnectTimeout = setTimeout(() => {
      this.connect()
    }, delay)
  }
  
  public send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected, cannot send:', data)
    }
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
  
  public disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
  
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
  
  public async requestAnalysis(data: { topic: string, [key: string]: any }): Promise<string> {
    try {
      // Import config dynamically
      const { getConfig } = require('./config')
      const { apiUrl } = getConfig()
      
      // Use the direct analysis endpoint
      const response = await fetch(`${apiUrl}/api/analysis-direct/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          depth: data.depth || 'comprehensive',
          ...data
        })
      })
      
      if (!response.ok) {
        throw new Error(`Analysis request failed: ${response.statusText}`)
      }
      
      const result = await response.json()
      
      // Also send via WebSocket for real-time updates
      if (this.isConnected()) {
        this.send({
          type: 'request_analysis',
          id: result.request_id,
          ...data
        })
      }
      
      return result.request_id
    } catch (error) {
      console.error('Failed to start analysis:', error)
      // Fallback to WebSocket-only method
      const requestId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      this.send({
        type: 'request_analysis',
        id: requestId,
        ...data
      })
      return requestId
    }
  }
}

// Create singleton
const simpleSocket = new SimpleWebSocket()

export default simpleSocket