'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Brain, TrendingUp, Users, Cpu, Building2, Lightbulb, ArrowRight, Sparkles, Activity } from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'

const agents = [
  {
    id: 'ai-futurist',
    name: 'AI & Agentic Futurist',
    icon: Brain,
    color: 'from-purple-500 to-pink-500',
    description: 'Tracks AI evolution and autonomous agent capabilities'
  },
  {
    id: 'trend-scanner',
    name: 'Trend Scanner',
    icon: TrendingUp,
    color: 'from-blue-500 to-cyan-500',
    description: 'Identifies weak signals across data sources'
  },
  {
    id: 'customer-insight',
    name: 'Customer Insight',
    icon: Users,
    color: 'from-green-500 to-emerald-500',
    description: 'Analyzes customer behavior evolution'
  },
  {
    id: 'tech-impact',
    name: 'Tech Impact',
    icon: Cpu,
    color: 'from-orange-500 to-red-500',
    description: 'Evaluates emerging technology implications'
  },
  {
    id: 'org-transformation',
    name: 'Org Transformation',
    icon: Building2,
    color: 'from-yellow-500 to-amber-500',
    description: 'Predicts organizational changes'
  },
  {
    id: 'synthesis',
    name: 'Synthesis',
    icon: Lightbulb,
    color: 'from-indigo-500 to-purple-500',
    description: 'Creates coherent scenarios and reports'
  }
]

export default function HomePage() {
  const { isConnected, connectionError } = useAgentStore()
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  if (!mounted) {
    return null // Prevent hydration mismatch
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background to-muted/20">
        <div className="container mx-auto px-4 py-20">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6"
            >
              <Sparkles className="w-4 h-4" />
              AI-Powered Customer Experience Insights
            </motion.div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                CX Futurist AI
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 leading-relaxed">
              Watch six specialized AI agents collaborate in real-time to analyze emerging trends, 
              predict customer behavior patterns, and generate actionable insights for the future of customer experience
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/analysis">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="group px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                >
                  Start Analysis
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              </Link>
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 border-2 border-primary text-primary rounded-lg font-medium hover:bg-primary/10 transition-colors"
                >
                  View Live Dashboard
                </motion.button>
              </Link>
            </div>
          </motion.div>
          
          {/* Animated background elements */}
          <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl" />
          </div>
        </div>
      </section>

      {/* Connection Status */}
      <section className="py-4 border-b">
        <div className="container mx-auto px-4">
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-center gap-4"
          >
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">System Status:</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : connectionError ? 'bg-red-500' : 'bg-yellow-500'} animate-pulse`} />
              <span className="text-sm font-medium">
                {isConnected ? 'All Systems Operational' : connectionError ? 'Connection Error' : 'Connecting to Backend...'}
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Agent Grid */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">Meet Your AI Agent Team</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Six specialized AI agents work together to analyze trends, predict patterns, and generate insights
            </p>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {agents.map((agent, index) => {
              const Icon = agent.icon
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  whileHover={{ scale: 1.02, y: -5 }}
                  className="relative group"
                >
                  <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl blur-xl"
                    style={{
                      background: `linear-gradient(to right, var(--tw-gradient-stops))`,
                      '--tw-gradient-from': agent.color.split(' ')[1],
                      '--tw-gradient-to': agent.color.split(' ')[3],
                    } as any}
                  />
                  <div className="relative bg-card border rounded-xl p-6 hover:border-primary/50 transition-colors">
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${agent.color} p-2.5 mb-4`}>
                      <Icon className="w-full h-full text-white" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground">{agent.description}</p>
                    <div className="mt-4 flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        <span>Ready</span>
                      </div>
                      <span className="text-xs text-muted-foreground">v2.0</span>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-muted/20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold mb-4">Powerful Features</h2>
            <p className="text-muted-foreground mb-12 max-w-2xl mx-auto">
              Experience the future of customer experience analysis with our cutting-edge visualization and AI capabilities
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              {[
                {
                  title: 'Live Agent Thinking',
                  description: 'Watch AI agents process information and generate insights in real-time'
                },
                {
                  title: '3D Knowledge Graph',
                  description: 'Explore interconnected insights through an interactive 3D visualization'
                },
                {
                  title: 'Trend Flow Analysis',
                  description: 'Track how weak signals evolve into strong trends over time'
                },
                {
                  title: 'Scenario Exploration',
                  description: 'Navigate multiple future scenarios with interactive timelines'
                }
              ].map((feature, i) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 + i * 0.1 }}
                  className="p-6 bg-card border rounded-lg hover:border-primary/50 transition-colors"
                >
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            className="max-w-2xl mx-auto"
          >
            <h2 className="text-3xl font-bold mb-4">Ready to Explore the Future?</h2>
            <p className="text-xl text-muted-foreground mb-8">
              Start your first analysis and see how AI can transform your understanding of customer experience trends
            </p>
            <Link href="/analysis">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="group px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transition-all inline-flex items-center gap-2"
              >
                Get Started Now
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}