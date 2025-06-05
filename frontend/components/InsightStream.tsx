'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Lightbulb, TrendingUp, AlertCircle, Sparkles } from 'lucide-react'
import { useAgentStore, type Insight } from '../stores/agentStore'
import { formatDate, getColorByScore, cn } from '../lib/utils'

const insightIcons = {
  breakthrough: Sparkles,
  trend: TrendingUp,
  warning: AlertCircle,
  general: Lightbulb
}

interface InsightStreamProps {
  className?: string
  limit?: number
  insights?: Insight[]
}

export default function InsightStream({ className, limit = 10, insights: propsInsights }: InsightStreamProps) {
  const storeInsights = useAgentStore((state) => state.insights)
  const insights = propsInsights || storeInsights
  
  // Get recent insights
  const recentInsights = insights.slice(0, limit)

  const getInsightType = (insight: any): keyof typeof insightIcons => {
    if (insight.confidence > 0.9) return 'breakthrough'
    if (insight.content.toLowerCase().includes('trend')) return 'trend'
    if (insight.content.toLowerCase().includes('risk') || 
        insight.content.toLowerCase().includes('challenge')) return 'warning'
    return 'general'
  }

  return (
    <div className={cn("bg-card border rounded-lg p-6", className)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Insight Stream</h2>
        <span className="text-sm text-muted-foreground">
          {insights.length} total
        </span>
      </div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        <AnimatePresence>
          {recentInsights.length > 0 ? (
            recentInsights.map((insight, index) => {
              const type = getInsightType(insight)
              const Icon = insightIcons[type]
              
              return (
                <motion.div
                  key={insight.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "p-4 rounded-lg border bg-background/50",
                    "hover:bg-background/80 transition-colors cursor-pointer"
                  )}
                >
                  {/* Header */}
                  <div className="flex items-start gap-3 mb-2">
                    <div className={cn(
                      "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                      type === 'breakthrough' && "bg-purple-500/10 text-purple-500",
                      type === 'trend' && "bg-blue-500/10 text-blue-500",
                      type === 'warning' && "bg-yellow-500/10 text-yellow-500",
                      type === 'general' && "bg-primary/10 text-primary"
                    )}>
                      <Icon className="w-4 h-4" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-primary">
                          {insight.agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className={cn(
                          "text-xs font-medium",
                          getColorByScore(insight.confidence)
                        )}>
                          {(insight.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      
                      {/* Content */}
                      <p className="text-sm text-foreground/90 leading-relaxed">
                        {insight.content}
                      </p>
                      
                      {/* Footer */}
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-xs text-muted-foreground">
                          {formatDate(insight.timestamp)}
                        </span>
                        
                        {insight.related && insight.related.length > 0 && (
                          <span className="text-xs text-muted-foreground">
                            {insight.related.length} related
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Lightbulb className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p className="text-sm">No insights generated yet</p>
              <p className="text-xs mt-1">Start an analysis to see insights</p>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Load More */}
      {insights.length > limit && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full mt-4 py-2 text-sm text-primary hover:text-primary/80 transition-colors"
        >
          View all insights →
        </motion.button>
      )}
    </div>
  )
}