// This file will be served statically and can be modified at runtime
// It allows us to inject environment-specific configuration without rebuilding

// Detect if we're running in production based on the hostname
const isProduction = typeof window !== 'undefined' && 
  (window.location.hostname.includes('run.app') || 
   window.location.hostname.includes('googleapis.com'));

window.__RUNTIME_CONFIG__ = {
  NEXT_PUBLIC_API_URL: isProduction 
    ? 'https://cx-futurist-api-4bgenndxea-uc.a.run.app'  // CX Futurist backend
    : (window.NEXT_PUBLIC_API_URL || 'http://localhost:8080'),
  NEXT_PUBLIC_WEBSOCKET_URL: isProduction
    ? 'wss://cx-futurist-api-4bgenndxea-uc.a.run.app'
    : (window.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8080')
};