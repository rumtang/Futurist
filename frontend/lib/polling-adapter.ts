// Polling adapter for agent status updates
import { getConfig } from './config'

export class PollingAdapter {
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private pollInterval: NodeJS.Timeout | null = null
  private isPolling = false
  
  constructor() {
    if (typeof window !== 'undefined') {
      this.startPolling()
    }
  }
  
  private async startPolling() {
    this.isPolling = true
    this.emit('connection:established', { connected: true })
    
    // Poll for updates every 2 seconds
    this.pollInterval = setInterval(async () => {
      if (!this.isPolling) return
      
      try {
        const { apiUrl } = getConfig()
        
        // Fetch agent status
        const response = await fetch(`${apiUrl}/api/agents/status`)
        if (response.ok) {
          const data = await response.json()
          
          // Emit system state
          this.emit('system:state', {
            agents: Object.entries(data.agents).reduce((acc, [id, agent]: [string, any]) => ({
              ...acc,
              [id]: {
                status: agent.status === 'ready' ? 'idle' : agent.status,
                last_active: agent.last_active || new Date().toISOString()
              }
            }), {}),
            system: {
              status: 'online',
              version: '1.0.0',
              capabilities: ['polling-updates']
            }
          })
          
          // Emit individual agent updates
          Object.entries(data.agents).forEach(([id, agent]: [string, any]) => {
            this.emit('agent:status', {
              agent: id,
              state: {
                status: agent.status === 'ready' ? 'idle' : agent.status,
                current_task: null
              }
            })
          })
        }
      } catch (error) {
        console.error('Polling error:', error)
        this.emit('connection:error', { error: 'Polling failed' })
      }
    }, 2000)
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
    console.log('Polling adapter send:', data)
  }
  
  public requestAnalysis(data: { topic: string, [key: string]: any }): string {
    const requestId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // Make API call to start analysis
    const { apiUrl } = getConfig()
    
    fetch(`${apiUrl}/api/analysis/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, request_id: requestId })
    }).then(response => {
      if (response.ok) {
        this.emit('analysis:started', { request_id: requestId })
      }
    }).catch(error => {
      console.error('Failed to start analysis:', error)
    })
    
    return requestId
  }
  
  public disconnect() {
    this.isPolling = false
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
      this.pollInterval = null
    }
    this.emit('connection:lost', { reason: 'Manual disconnect' })
  }
  
  public isConnected(): boolean {
    return this.isPolling
  }
}

// Create singleton
const pollingAdapter = new PollingAdapter()

export default pollingAdapter