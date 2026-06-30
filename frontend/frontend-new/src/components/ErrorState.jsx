import { AlertTriangle, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'

export default function ErrorState({ message, onRetry }) {
  return (
    <motion.div
      className="error-state"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <AlertTriangle size={48} className="error-icon" />
      <h3>Something went wrong</h3>
      <p>{message || 'An unexpected error occurred. Please try again.'}</p>
      {onRetry && (
        <button className="btn btn-secondary" onClick={onRetry}>
          <RefreshCw size={16} />
          <span>Try Again</span>
        </button>
      )}
    </motion.div>
  )
}
