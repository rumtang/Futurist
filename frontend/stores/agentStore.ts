import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import socketClient from '../lib/simple-socket'

export interface AgentState {
  id: string
  name: string
  status: 'idle' | 'thinking' | 'analyzing' | 'collaborating' | 'error'
  currentTask: string | null
  thoughts: Array<{
    content: string
    confidence: number
    timestamp: number
  }>
  collaborations: Array<{
    with: string
    message: string
    timestamp: number
  }>
  lastActive: string | null
}

export interface Insight {
  id: string
  agent: string
  content: string
  confidence: number
  timestamp: string
  related: string[]
}

export interface TrendSignal {
  id: string
  name: string
  strength: number
  trajectory: 'rising' | 'stable' | 'declining'
  sources: string[]
  timestamp: string
}

interface AgentStore {
  // Connection state
  isConnected: boolean
  connectionError: string | null
  
  // Agent states
  agents: Record<string, AgentState>
  
  // Insights
  insights: Insight[]
  
  // Trends
  trends: TrendSignal[]
  
  // Active analysis
  activeAnalysis: {
    id: string | null
    topic: string | null
    status: 'idle' | 'running' | 'completed' | 'error'
    progress: number
    startTime: string | null
    results: any | null
  }
  
  // Actions
  connect: () => void
  disconnect: () => void
  updateAgentState: (agentId: string, update: Partial<AgentState>) => void
  addInsight: (insight: Insight) => void
  updateTrend: (trend: TrendSignal) => void
  startAnalysis: (topic: string, options?: any) => Promise<string>
  updateAnalysisProgress: (progress: number) => void
  completeAnalysis: (results: any) => void
  reset: () => void
}

const initialAgents: Record<string, AgentState> = {
  'ai_futurist': {
    id: 'ai_futurist',
    name: 'AI & Agentic Futurist',
    status: 'idle',
    currentTask: null,
    thoughts: [],
    collaborations: [],
    lastActive: null
  },
  'trend_scanner': {
    id: 'trend_scanner',
    name: 'Trend Scanner',
    status: 'idle',
    currentTask: null,
    thoughts: [],
    collaborations: [],
    lastActive: null
  },
  'customer_insight': {
    id: 'customer_insight',
    name: 'Customer Insight',
    status: 'idle',
    currentTask: null,
    thoughts: [],
    collaborations: [],
    lastActive: null
  },
  'tech_impact': {
    id: 'tech_impact',
    name: 'Tech Impact',
    status: 'idle',
    currentTask: null,
    thoughts: [],
    collaborations: [],
    lastActive: null
  },
  'org_transformation': {
    id: 'org_transformation',
    name: 'Org Transformation',
    status: 'idle',
    currentTask: null,
    thoughts: [],
    collaborations: [],
    lastActive: null
  },
  'synthesis': {
    id: 'synthesis',
    name: 'Synthesis',
    status: 'idle',
    currentTask: null,
    thoughts: [],
    collaborations: [],
    lastActive: null
  }
}

export const useAgentStore = create<AgentStore>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    isConnected: false,
    connectionError: null,
    agents: initialAgents,
    insights: [],
    trends: [],
    activeAnalysis: {
      id: null,
      topic: null,
      status: 'idle',
      progress: 0,
      startTime: null,
      results: null
    },
    
    // Actions
    connect: () => {
      try {
        // Set up socket event listeners
        socketClient.on('connection:established', () => {
          set({ isConnected: true, connectionError: null })
        })
        
        socketClient.on('connection:lost', ({ reason }) => {
          set({ isConnected: false, connectionError: reason })
        })
        
        socketClient.on('connection:failed', ({ error }) => {
          set({ isConnected: false, connectionError: error || 'Connection failed' })
        })
        
        socketClient.on('connection:error', ({ error }) => {
          set({ isConnected: false, connectionError: 'Connection error' })
        })
      
      socketClient.on('system:state', (data) => {
        // Update agent states from system state
        const updates: Record<string, Partial<AgentState>> = {}
        Object.entries(data.agents).forEach(([id, state]: [string, any]) => {
          updates[id] = {
            status: state.status,
            lastActive: state.last_active
          }
        })
        
        set(state => ({
          agents: Object.keys(state.agents).reduce((acc, id) => ({
            ...acc,
            [id]: { ...state.agents[id], ...updates[id] }
          }), {})
        }))
      })
      
      // Agent event handlers
      socketClient.on('agent:status', (data) => {
        get().updateAgentState(data.agent, {
          status: data.state.status,
          currentTask: data.state.current_task
        })
      })
      
      socketClient.on('agent:thought', (data) => {
        set(state => ({
          agents: {
            ...state.agents,
            [data.agent]: {
              ...state.agents[data.agent],
              thoughts: [
                ...state.agents[data.agent].thoughts.slice(-19), // Keep last 20
                data.thought
              ],
              lastActive: new Date().toISOString()
            }
          }
        }))
      })
      
      socketClient.on('agent:collaboration', (data) => {
        set(state => ({
          agents: {
            ...state.agents,
            [data.agent]: {
              ...state.agents[data.agent],
              collaborations: [
                ...state.agents[data.agent].collaborations.slice(-9), // Keep last 10
                data.collaboration
              ]
            }
          }
        }))
      })
      
      // Insight handlers
      socketClient.on('insight:generated', (data) => {
        get().addInsight({
          id: `insight_${Date.now()}`,
          agent: data.agent,
          content: data.content,
          confidence: data.confidence || 0.8,
          timestamp: new Date().toISOString(),
          related: data.related || []
        })
      })
      
      // Trend handlers
      socketClient.on('trend:update', (data) => {
        get().updateTrend({
          id: data.id || `trend_${Date.now()}`,
          name: data.signal,
          strength: data.strength,
          trajectory: data.trajectory,
          sources: data.sources || [],
          timestamp: data.timestamp
        })
      })
      
      // Analysis handlers
      socketClient.on('analysis:started', (data) => {
        set({
          activeAnalysis: {
            id: data.request_id,
            topic: data.topic || get().activeAnalysis.topic,
            status: 'running',
            progress: 0,
            startTime: new Date().toISOString(),
            results: null
          }
        })
      })
      
      socketClient.on('analysis:progress', (data) => {
        get().updateAnalysisProgress(data.progress || 0)
      })
      
      socketClient.on('analysis:completed', (data) => {
        get().completeAnalysis(data.results)
      })
      } catch (error) {
        console.error('Error setting up socket connection:', error)
        set({ isConnected: false, connectionError: 'Setup error' })
      }
    },
    
    disconnect: () => {
      socketClient.disconnect()
      set({ isConnected: false })
    },
    
    updateAgentState: (agentId, update) => {
      set(state => ({
        agents: {
          ...state.agents,
          [agentId]: {
            ...state.agents[agentId],
            ...update,
            lastActive: new Date().toISOString()
          }
        }
      }))
    },
    
    addInsight: (insight) => {
      set(state => ({
        insights: [insight, ...state.insights].slice(0, 100) // Keep last 100
      }))
    },
    
    updateTrend: (trend) => {
      set(state => {
        const existingIndex = state.trends.findIndex(t => t.id === trend.id)
        if (existingIndex >= 0) {
          const newTrends = [...state.trends]
          newTrends[existingIndex] = trend
          return { trends: newTrends }
        } else {
          return { trends: [trend, ...state.trends].slice(0, 50) } // Keep last 50
        }
      })
    },
    
    startAnalysis: async (topic, options = {}) => {
      try {
        const requestId = await socketClient.requestAnalysis({
          topic,
          ...options
        })
        
        set({
          activeAnalysis: {
            id: requestId,
            topic,
            status: 'running',
            progress: 0,
            startTime: new Date().toISOString(),
            results: null
          }
        })
        
        return requestId
      } catch (error) {
        set(state => ({
          activeAnalysis: {
            ...state.activeAnalysis,
            status: 'error'
          }
        }))
        throw error
      }
    },
    
    updateAnalysisProgress: (progress) => {
      set(state => ({
        activeAnalysis: {
          ...state.activeAnalysis,
          progress: Math.min(100, Math.max(0, progress))
        }
      }))
    },
    
    completeAnalysis: (results) => {
      set(state => ({
        activeAnalysis: {
          ...state.activeAnalysis,
          status: 'completed',
          progress: 100,
          results
        }
      }))
    },
    
    reset: () => {
      set({
        agents: initialAgents,
        insights: [],
        trends: [],
        activeAnalysis: {
          id: null,
          topic: null,
          status: 'idle',
          progress: 0,
          startTime: null,
          results: null
        }
      })
    }
  }))
)

// Auto-connect on store creation
if (typeof window !== 'undefined') {
  useAgentStore.getState().connect()
}