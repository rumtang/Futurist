'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Loader2, Sparkles, Settings2 } from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'
import { cn } from '../lib/utils'

interface AnalysisControlProps {
  className?: string
}

export default function AnalysisControl({ className }: AnalysisControlProps) {
  const { startAnalysis, activeAnalysis } = useAgentStore()
  const [topic, setTopic] = useState('')
  const [depth, setDepth] = useState('comprehensive')
  const [timeframe, setTimeframe] = useState('5-10 years')
  const [showAdvanced, setShowAdvanced] = useState(false)

  const isAnalyzing = activeAnalysis.status === 'running'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim() || isAnalyzing) return

    try {
      await startAnalysis(topic, {
        depth,
        timeframe
      })
      setTopic('')
    } catch (error) {
      console.error('Failed to start analysis:', error)
    }
  }

  const suggestedTopics = [
    "AI agents in customer service",
    "Future of personalization",
    "Gen Z shopping behaviors",
    "Voice commerce evolution",
    "Sustainable customer experiences"
  ]

  return (
    <div className={cn("bg-gray-800 border border-gray-700 rounded-lg p-6", className)} style={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white" style={{ color: '#FFFFFF', fontSize: '1.25rem' }}>Start Analysis</h2>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <Settings2 className="w-4 h-4" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Topic Input */}
        <div>
          <label className="text-sm font-medium mb-2 block text-gray-200" style={{ color: '#E5E7EB' }}>
            What would you like to analyze?
          </label>
          <div className="relative">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Future of AI in customer experience"
              disabled={isAnalyzing}
              className={cn(
                "w-full px-4 py-2 pr-10 rounded-lg border border-gray-600 bg-gray-700 text-white",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
              style={{ 
                backgroundColor: '#374151',
                borderColor: '#4B5563',
                color: '#FFFFFF'
              }}
            />
            <Search className="absolute right-3 top-2.5 w-5 h-5 text-gray-400" style={{ color: '#9CA3AF' }} />
          </div>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4"
          >
            {/* Analysis Depth */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Analysis Depth
              </label>
              <select
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
                disabled={isAnalyzing}
                className={cn(
                  "w-full px-4 py-2 rounded-lg border bg-background",
                  "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                <option value="quick">Quick Overview</option>
                <option value="standard">Standard Analysis</option>
                <option value="comprehensive">Comprehensive Deep Dive</option>
              </select>
            </div>

            {/* Timeframe */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Future Timeframe
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                disabled={isAnalyzing}
                className={cn(
                  "w-full px-4 py-2 rounded-lg border bg-background",
                  "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                <option value="1-2 years">Near-term (1-2 years)</option>
                <option value="3-5 years">Mid-term (3-5 years)</option>
                <option value="5-10 years">Long-term (5-10 years)</option>
                <option value="10+ years">Far future (10+ years)</option>
              </select>
            </div>
          </motion.div>
        )}

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={!topic.trim() || isAnalyzing}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={cn(
            "w-full py-3 rounded-lg font-medium transition-all",
            "bg-blue-600 text-white",
            "hover:bg-blue-700",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "flex items-center justify-center gap-2"
          )}
          style={{
            backgroundColor: isAnalyzing || !topic.trim() ? '#4B5563' : '#2563EB',
            color: '#FFFFFF'
          }}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Start Analysis
            </>
          )}
        </motion.button>
      </form>

      {/* Suggested Topics */}
      {!isAnalyzing && topic.length === 0 && (
        <div className="mt-6">
          <p className="text-sm text-gray-300 mb-2" style={{ color: '#D1D5DB' }}>Suggested topics:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedTopics.map((suggestion) => (
              <motion.button
                key={suggestion}
                onClick={() => setTopic(suggestion)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  "px-3 py-1 text-xs rounded-full",
                  "bg-blue-500/20 text-blue-300",
                  "hover:bg-blue-500/30 transition-colors"
                )}
                style={{
                  backgroundColor: '#1D4ED8',
                  color: '#93C5FD'
                }}
              >
                {suggestion}
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}