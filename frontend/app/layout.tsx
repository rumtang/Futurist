import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CX Futurist AI - Visualizing the Future of Customer Experience',
  description: 'Watch AI agents analyze emerging trends and predict the future of customer interactions in real-time',
  keywords: 'AI, customer experience, future trends, multi-agent system, real-time analysis',
  authors: [{ name: 'CX Futurist Team' }],
  openGraph: {
    title: 'CX Futurist AI',
    description: 'Multi-agent AI system analyzing the future of customer experience',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <script src="/runtime-config.js" />
      </head>
      <body className={`${inter.className} min-h-screen bg-background antialiased`}>
        <div className="relative flex min-h-screen flex-col">
          <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center">
              <div className="mr-4 flex">
                <a className="mr-6 flex items-center space-x-2" href="/">
                  <span className="font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
                    CX Futurist AI
                  </span>
                </a>
              </div>
              <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                <nav className="flex items-center space-x-6 text-sm font-medium">
                  <a href="/dashboard" className="transition-colors hover:text-foreground/80">
                    Dashboard
                  </a>
                  <a href="/analysis" className="transition-colors hover:text-foreground/80">
                    Analysis
                  </a>
                  <a href="/knowledge" className="transition-colors hover:text-foreground/80">
                    Knowledge Graph
                  </a>
                  <a href="/scenarios" className="transition-colors hover:text-foreground/80">
                    Scenarios
                  </a>
                </nav>
              </div>
            </div>
          </header>
          <main className="flex-1">{children}</main>
        </div>
      </body>
    </html>
  )
}