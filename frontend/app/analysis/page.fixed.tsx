'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { ArrowLeft, AlertCircle, CheckCircle2, Info } from 'lucide-react'
import AnalysisControl from '../../components/AnalysisControl'
import InsightStream from '../../components/InsightStream'
import { useAgentStore } from '../../stores/agentStore'

export default function AnalysisPage() {
  const [mounted, setMounted] = useState(false)
  
  // Use the hook properly at the top level
  const activeAnalysis = useAgentStore(state => state.activeAnalysis)
  const insights = useAgentStore(state => state.insights)
  const isConnected = useAgentStore(state => state.isConnected)
  const connectionError = useAgentStore(state => state.connectionError)
  const agents = useAgentStore(state => state.agents)
  
  useEffect(() => {
    setMounted(true)
    console.log('Analysis page mounted')
    console.log('Store state:', { activeAnalysis, insights, isConnected, connectionError, agents })
  }, [activeAnalysis, insights, isConnected, connectionError, agents])
  
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4 text-white">Loading Analysis Page...</h1>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Navigation */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link href="/" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </motion.div>

        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
            Start Your Analysis
          </h1>
          <p className="text-xl text-gray-300">
            Enter a topic to analyze future trends and customer experience implications
          </p>
        </motion.div>

        {/* Connection Warning */}
        {!isConnected && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-medium text-yellow-500 mb-1">
                  {connectionError ? 'Connection Error' : 'Connecting to Backend...'}
                </h3>
                <p className="text-sm text-gray-300">
                  {connectionError 
                    ? `Unable to connect to the analysis backend. Error: ${connectionError}` 
                    : 'Establishing connection with AI agents. This may take a few moments...'}
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Analysis Input */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <AnalysisControl />
            
            {/* Active Agents Status */}
            {activeAnalysis?.status === 'running' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-6 bg-gray-800 border border-gray-700 rounded-lg p-6"
              >
                <h3 className="font-semibold mb-4 text-white">Agent Activity</h3>
                <div className="space-y-3">
                  {Object.values(agents || {}).map((agent: any) => (
                    <div key={agent.id} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          agent.status === 'thinking' || agent.status === 'analyzing' 
                            ? 'bg-blue-500 animate-pulse' 
                            : agent.status === 'collaborating'
                            ? 'bg-purple-500 animate-pulse'
                            : agent.status === 'error'
                            ? 'bg-red-500'
                            : 'bg-gray-400'
                        }`} />
                        <span className="text-sm font-medium text-gray-200">{agent.name}</span>
                      </div>
                      <span className="text-xs text-gray-400 capitalize">
                        {agent.status === 'idle' ? 'waiting' : agent.status}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Right Column - Results */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <AnimatePresence mode="wait">
              {activeAnalysis?.status === 'completed' && activeAnalysis?.results ? (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="bg-gray-800 border border-gray-700 rounded-lg p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    <h2 className="text-xl font-semibold text-white">Analysis Complete</h2>
                  </div>
                  
                  {/* Formatted Results */}
                  <div className="space-y-6">
                    {activeAnalysis.results.summary && (
                      <div>
                        <h3 className="font-medium mb-2 text-gray-200">Executive Summary</h3>
                        <p className="text-sm text-gray-400 leading-relaxed">
                          {activeAnalysis.results.summary}
                        </p>
                      </div>
                    )}
                    
                    {activeAnalysis.results.key_insights && (
                      <div>
                        <h3 className="font-medium mb-2 text-gray-200">Key Insights</h3>
                        <ul className="space-y-2">
                          {activeAnalysis.results.key_insights.map((insight: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-400">
                              <span className="text-blue-500 mt-1">•</span>
                              <span>{insight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {activeAnalysis.results.recommendations && (
                      <div>
                        <h3 className="font-medium mb-2 text-gray-200">Recommendations</h3>
                        <ul className="space-y-2">
                          {activeAnalysis.results.recommendations.map((rec: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-400">
                              <span className="text-green-500 mt-1">→</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Raw Results Fallback */}
                    {!activeAnalysis.results.summary && !activeAnalysis.results.key_insights && (
                      <div>
                        <h3 className="font-medium mb-2 text-gray-200">Analysis Results</h3>
                        <pre className="whitespace-pre-wrap text-sm text-gray-400 bg-gray-900 rounded p-4 overflow-x-auto">
                          {typeof activeAnalysis.results === 'string' 
                            ? activeAnalysis.results 
                            : JSON.stringify(activeAnalysis.results, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </motion.div>
              ) : activeAnalysis?.status === 'running' ? (
                <motion.div
                  key="progress"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  {/* Progress Card */}
                  <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4 text-white">Analysis in Progress</h2>
                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-sm text-gray-400">
                            Analyzing: <span className="font-medium text-gray-200">{activeAnalysis.topic}</span>
                          </p>
                          <span className="text-sm font-medium text-gray-200">{activeAnalysis.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                          <motion.div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${activeAnalysis.progress}%` }}
                            transition={{ duration: 0.5, ease: "easeOut" }}
                          />
                        </div>
                      </div>
                      
                      {/* Status Messages */}
                      <div className="space-y-2">
                        {activeAnalysis.progress < 20 && (
                          <p className="text-xs text-gray-400">Initializing AI agents...</p>
                        )}
                        {activeAnalysis.progress >= 20 && activeAnalysis.progress < 40 && (
                          <p className="text-xs text-gray-400">Scanning for emerging trends...</p>
                        )}
                        {activeAnalysis.progress >= 40 && activeAnalysis.progress < 60 && (
                          <p className="text-xs text-gray-400">Analyzing customer behavior patterns...</p>
                        )}
                        {activeAnalysis.progress >= 60 && activeAnalysis.progress < 80 && (
                          <p className="text-xs text-gray-400">Evaluating technology implications...</p>
                        )}
                        {activeAnalysis.progress >= 80 && (
                          <p className="text-xs text-gray-400">Synthesizing insights and generating report...</p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Live Insights */}
                  {insights.length > 0 && <InsightStream insights={insights.slice(0, 5)} />}
                </motion.div>
              ) : activeAnalysis?.status === 'error' ? (
                <motion.div
                  key="error"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="bg-gray-800 border border-red-500/50 rounded-lg p-6"
                >
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <h2 className="text-xl font-semibold text-red-500 mb-2">Analysis Error</h2>
                      <p className="text-sm text-gray-400 mb-4">
                        An error occurred while processing your analysis. Please try again or contact support if the issue persists.
                      </p>
                      <button
                        onClick={() => window.location.reload()}
                        className="text-sm text-blue-500 hover:underline"
                      >
                        Refresh page and try again
                      </button>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="instructions"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="bg-gray-800 border border-gray-700 rounded-lg p-6"
                >
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <h2 className="text-xl font-semibold mb-4 text-white">How it Works</h2>
                      <div className="space-y-4 text-sm text-gray-400">
                        <div>
                          <h3 className="font-medium text-gray-200 mb-1">1. Enter Your Topic</h3>
                          <p>Describe what aspect of customer experience you want to analyze. Be specific about the industry, technology, or trend you're interested in.</p>
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-200 mb-1">2. AI Agents Collaborate</h3>
                          <p>Six specialized agents work together to analyze trends, customer behaviors, technologies, and organizational implications.</p>
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-200 mb-1">3. Real-time Insights</h3>
                          <p>Watch as insights are generated in real-time. Each agent contributes their unique perspective to build a comprehensive analysis.</p>
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-200 mb-1">4. Comprehensive Report</h3>
                          <p>Receive a detailed analysis with key insights, future scenarios, and actionable recommendations for your organization.</p>
                        </div>
                      </div>
                      
                      <div className="mt-6 p-4 bg-gray-900 rounded-lg">
                        <p className="text-xs text-gray-500">
                          <strong>Pro tip:</strong> Try topics like "AI-powered personalization in retail", 
                          "Voice commerce adoption", or "Sustainable packaging impact on CX"
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  )
}