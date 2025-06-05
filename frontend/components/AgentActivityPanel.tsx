'use client'

import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, TrendingUp, Users, Cpu, Building2, Lightbulb, Activity, Loader2 } from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'
import { cn } from '../lib/utils'

const agentIcons = {
  ai_futurist: Brain,
  trend_scanner: TrendingUp,
  customer_insight: Users,
  tech_impact: Cpu,
  org_transformation: Building2,
  synthesis: Lightbulb
}

const agentColors = {
  ai_futurist: 'from-purple-500 to-pink-500',
  trend_scanner: 'from-blue-500 to-cyan-500',
  customer_insight: 'from-green-500 to-emerald-500',
  tech_impact: 'from-orange-500 to-red-500',
  org_transformation: 'from-yellow-500 to-amber-500',
  synthesis: 'from-indigo-500 to-purple-500'
}

interface AgentActivityPanelProps {
  className?: string
  showThoughts?: boolean
  showCollaborations?: boolean
}

export default function AgentActivityPanel({ 
  className, 
  showThoughts = true,
  showCollaborations = true 
}: AgentActivityPanelProps) {
  const { agents, isConnected } = useAgentStore()
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  return (
    <div className={cn("bg-card border rounded-lg p-6", className)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Agent Activity</h2>
        <div className="flex items-center gap-2 text-sm">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isConnected ? "bg-green-500" : "bg-red-500"
          )} />
          <span className="text-muted-foreground">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        {Object.entries(agents).map(([agentId, agent]) => {
          const Icon = agentIcons[agentId as keyof typeof agentIcons]
          const colorClass = agentColors[agentId as keyof typeof agentColors]
          const isActive = agent.status !== 'idle'
          const isSelected = selectedAgent === agentId

          return (
            <motion.div
              key={agentId}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedAgent(isSelected ? null : agentId)}
              className={cn(
                "relative p-4 rounded-lg border cursor-pointer transition-all",
                isSelected ? "border-primary bg-primary/5" : "border-border hover:border-primary/50",
                isActive && "ring-2 ring-primary/20"
              )}
            >
              {/* Agent Icon */}
              <div className={cn(
                "w-10 h-10 rounded-lg p-2 mb-2",
                `bg-gradient-to-br ${colorClass}`,
                isActive && "animate-pulse"
              )}>
                <Icon className="w-full h-full text-white" />
              </div>

              {/* Agent Name */}
              <h3 className="font-medium text-sm mb-1">{agent.name}</h3>

              {/* Status */}
              <div className="flex items-center gap-1.5">
                {agent.status === 'thinking' && (
                  <Loader2 className="w-3 h-3 animate-spin text-primary" />
                )}
                <span className={cn(
                  "text-xs capitalize",
                  agent.status === 'idle' ? "text-muted-foreground" : "text-primary"
                )}>
                  {agent.status}
                </span>
              </div>

              {/* Current Task */}
              {agent.currentTask && (
                <p className="text-xs text-muted-foreground mt-1 truncate">
                  {agent.currentTask}
                </p>
              )}

              {/* Activity Indicator */}
              {isActive && (
                <motion.div
                  className="absolute top-2 right-2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                >
                  <Activity className="w-4 h-4 text-primary" />
                </motion.div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Selected Agent Details */}
      <AnimatePresence>
        {selectedAgent && agents[selectedAgent] && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t pt-4"
          >
            <h3 className="font-medium mb-3">
              {agents[selectedAgent].name} Details
            </h3>

            {/* Thoughts Stream */}
            {showThoughts && agents[selectedAgent].thoughts.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium mb-2">Recent Thoughts</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {agents[selectedAgent].thoughts.slice(-5).reverse().map((thought, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="text-sm p-2 bg-muted/50 rounded"
                    >
                      <p className="text-foreground/80">{thought.content}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted-foreground">
                          Confidence: {(thought.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Collaborations */}
            {showCollaborations && agents[selectedAgent].collaborations.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2">Collaborations</h4>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {agents[selectedAgent].collaborations.slice(-3).reverse().map((collab, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="text-sm p-2 bg-muted/30 rounded flex items-start gap-2"
                    >
                      <span className="text-primary font-medium">→</span>
                      <div className="flex-1">
                        <span className="font-medium">{collab.with}:</span>
                        <span className="text-foreground/70 ml-1">{collab.message}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}