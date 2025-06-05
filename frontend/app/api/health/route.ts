import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check if we can reach the backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
    let backendStatus = 'unknown'
    let backendError = null
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
      
      const response = await fetch(`${backendUrl}/health`, {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
        },
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        backendStatus = 'healthy'
      } else {
        backendStatus = 'unhealthy'
        backendError = `Backend returned status ${response.status}`
      }
    } catch (error) {
      backendStatus = 'unreachable'
      backendError = error instanceof Error ? error.message : 'Unknown error'
    }
    
    return NextResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      frontend: {
        status: 'healthy',
        version: '1.0.0',
      },
      backend: {
        status: backendStatus,
        url: backendUrl,
        error: backendError,
      },
      websocket: {
        url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8080',
      },
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}