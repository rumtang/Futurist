// Configuration helper for frontend

declare global {
  interface Window {
    __RUNTIME_CONFIG__?: {
      NEXT_PUBLIC_API_URL?: string
      NEXT_PUBLIC_WEBSOCKET_URL?: string
    }
  }
}

export function getConfig() {
  // Check for runtime config first (for client-side)
  if (typeof window !== 'undefined' && window.__RUNTIME_CONFIG__) {
    const apiUrl = window.__RUNTIME_CONFIG__.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
    const websocketUrl = window.__RUNTIME_CONFIG__.NEXT_PUBLIC_WEBSOCKET_URL || process.env.NEXT_PUBLIC_WEBSOCKET_URL || apiUrl.replace(/^https:/, 'wss:').replace(/^http:/, 'ws:')
    
    return {
      apiUrl,
      websocketUrl
    }
  }
  
  // Fall back to build-time env vars (for server-side)
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
  
  // Convert to WebSocket URL
  let websocketUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || apiUrl
  
  // If websocket URL is not explicitly set, derive it from API URL
  if (!process.env.NEXT_PUBLIC_WEBSOCKET_URL) {
    websocketUrl = apiUrl
      .replace(/^https:/, 'wss:')
      .replace(/^http:/, 'ws:')
  }
  
  return {
    apiUrl,
    websocketUrl
  }
}