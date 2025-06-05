import { NextResponse } from 'next/server'

export async function GET() {
  // Return current configuration (sanitized for security)
  return NextResponse.json({
    environment: process.env.NODE_ENV || 'development',
    api: {
      url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
      configured: !!process.env.NEXT_PUBLIC_API_URL,
    },
    websocket: {
      url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8080',
      configured: !!process.env.NEXT_PUBLIC_WEBSOCKET_URL,
    },
    runtime: {
      node: process.version,
      platform: process.platform,
    },
    timestamp: new Date().toISOString(),
  })
}