'use client'

import { motion } from 'framer-motion'

export default function KnowledgePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold mb-2">Knowledge Graph</h1>
        <p className="text-muted-foreground">
          Interactive visualization of connected insights and trends
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-card border rounded-lg p-12 text-center"
      >
        <p className="text-xl text-muted-foreground">
          Knowledge graph visualization coming soon...
        </p>
        <p className="text-sm text-muted-foreground mt-4">
          This will display an interactive 3D graph showing relationships between insights, trends, and predictions.
        </p>
      </motion.div>
    </div>
  )
}