'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'
import { cn, getStrengthLabel } from '../lib/utils'

interface TrendFlowChartProps {
  className?: string
}

export default function TrendFlowChart({ className }: TrendFlowChartProps) {
  const { trends } = useAgentStore()
  
  // Get top trends
  const topTrends = trends.slice(0, 8)

  const getTrendIcon = (trajectory: string) => {
    switch (trajectory) {
      case 'rising':
        return TrendingUp
      case 'declining':
        return TrendingDown
      case 'stable':
        return Minus
      default:
        return Activity
    }
  }

  const getTrendColor = (strength: number, trajectory: string) => {
    if (trajectory === 'declining') return 'text-red-500 bg-red-500/10'
    if (strength >= 0.8) return 'text-green-500 bg-green-500/10'
    if (strength >= 0.6) return 'text-blue-500 bg-blue-500/10'
    if (strength >= 0.4) return 'text-yellow-500 bg-yellow-500/10'
    return 'text-gray-500 bg-gray-500/10'
  }

  return (
    <div className={cn("bg-card border rounded-lg p-6", className)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Trend Flow</h2>
        <span className="text-sm text-muted-foreground">
          Live trends
        </span>
      </div>

      {topTrends.length > 0 ? (
        <div className="space-y-3">
          {topTrends.map((trend, index) => {
            const Icon = getTrendIcon(trend.trajectory)
            const colorClass = getTrendColor(trend.strength, trend.trajectory)
            
            return (
              <motion.div
                key={trend.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-3 p-3 rounded-lg bg-background/50 hover:bg-background/80 transition-colors cursor-pointer"
              >
                {/* Trend Icon */}
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center",
                  colorClass
                )}>
                  <Icon className="w-5 h-5" />
                </div>

                {/* Trend Info */}
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm truncate">{trend.name}</h4>
                  <div className="flex items-center gap-4 mt-1">
                    <span className="text-xs text-muted-foreground">
                      {getStrengthLabel(trend.strength)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {trend.sources.length} sources
                    </span>
                  </div>
                </div>

                {/* Strength Visualization */}
                <div className="w-24">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-muted-foreground">Strength</span>
                    <span className="text-xs font-medium">
                      {(trend.strength * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <motion.div
                      className={cn(
                        "h-1.5 rounded-full",
                        trend.trajectory === 'declining' ? 'bg-red-500' :
                        trend.strength >= 0.8 ? 'bg-green-500' :
                        trend.strength >= 0.6 ? 'bg-blue-500' :
                        trend.strength >= 0.4 ? 'bg-yellow-500' :
                        'bg-gray-500'
                      )}
                      initial={{ width: 0 }}
                      animate={{ width: `${trend.strength * 100}%` }}
                      transition={{ duration: 0.5, delay: index * 0.05 }}
                    />
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <Activity className="w-12 h-12 mx-auto mb-3 opacity-20" />
          <p className="text-sm">No trends detected yet</p>
          <p className="text-xs mt-1">Run an analysis to discover trends</p>
        </div>
      )}

      {/* View All Button */}
      {trends.length > topTrends.length && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full mt-4 py-2 text-sm text-primary hover:text-primary/80 transition-colors"
        >
          View all {trends.length} trends →
        </motion.button>
      )}

      {/* Flow Animation */}
      <svg className="absolute inset-0 pointer-events-none opacity-10" aria-hidden="true">
        <defs>
          <pattern id="flow-pattern" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" className="fill-primary">
              <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" />
            </circle>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#flow-pattern)" />
      </svg>
    </div>
  )
}