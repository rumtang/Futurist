'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import AgentActivityPanel from '../../components/AgentActivityPanel'
import InsightStream from '../../components/InsightStream'
import TrendFlowChart from '../../components/TrendFlowChart'
import AnalysisControl from '../../components/AnalysisControl'
import { useAgentStore } from '../../stores/agentStore'

export default function DashboardPage() {
  const { isConnected, activeAnalysis } = useAgentStore()

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold mb-2">CX Futurist Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time visualization of AI agents analyzing the future of customer experience
        </p>
      </motion.div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column - Agent Activity */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-4"
        >
          <AgentActivityPanel className="h-full" />
        </motion.div>

        {/* Middle Column - Analysis & Trends */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-5 space-y-6"
        >
          {/* Analysis Control */}
          <AnalysisControl />

          {/* Active Analysis Progress */}
          {activeAnalysis.status === 'running' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-card border rounded-lg p-6"
            >
              <h3 className="font-semibold mb-2">Analysis in Progress</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Topic: {activeAnalysis.topic}
              </p>
              <div className="w-full bg-muted rounded-full h-2">
                <motion.div
                  className="bg-primary rounded-full h-2"
                  initial={{ width: 0 }}
                  animate={{ width: `${activeAnalysis.progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {activeAnalysis.progress}% complete
              </p>
            </motion.div>
          )}

          {/* Trend Flow */}
          <TrendFlowChart />
        </motion.div>

        {/* Right Column - Insights */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-3"
        >
          <InsightStream />
        </motion.div>
      </div>

      {/* Bottom Row - Additional Visualizations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6"
      >
        {/* Quick Stats */}
        <div className="bg-card border rounded-lg p-6">
          <h3 className="font-semibold mb-4">System Stats</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Active Agents</span>
              <span className="text-sm font-medium">6/6</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Analyses Today</span>
              <span className="text-sm font-medium">12</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Insights Generated</span>
              <span className="text-sm font-medium">47</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Trends Tracked</span>
              <span className="text-sm font-medium">23</span>
            </div>
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="bg-card border rounded-lg p-6">
          <h3 className="font-semibold mb-4">Recent Analyses</h3>
          <div className="space-y-2">
            <div className="text-sm">
              <p className="font-medium">AI in Customer Service</p>
              <p className="text-xs text-muted-foreground">2 hours ago</p>
            </div>
            <div className="text-sm">
              <p className="font-medium">Gen Z Shopping Behaviors</p>
              <p className="text-xs text-muted-foreground">5 hours ago</p>
            </div>
            <div className="text-sm">
              <p className="font-medium">Future of Personalization</p>
              <p className="text-xs text-muted-foreground">1 day ago</p>
            </div>
          </div>
        </div>

        {/* Top Trends */}
        <div className="bg-card border rounded-lg p-6">
          <h3 className="font-semibold mb-4">Top Trends</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">AI Agents</span>
              <span className="text-xs text-green-500">↑ 85%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Voice Commerce</span>
              <span className="text-xs text-green-500">↑ 72%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Sustainable CX</span>
              <span className="text-xs text-yellow-500">↑ 45%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">AR Shopping</span>
              <span className="text-xs text-yellow-500">↑ 38%</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}