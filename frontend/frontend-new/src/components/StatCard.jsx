import { motion } from 'framer-motion'

export default function StatCard({ icon: Icon, label, value, delay = 0, color = 'var(--brand)' }) {
  return (
    <motion.div
      className="card stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
    >
      <div
        className="stat-card-icon"
        style={{ background: `${color}15`, color }}
      >
        <Icon size={22} />
      </div>
      <div className="stat-card-value">{value}</div>
      <div className="stat-card-label">{label}</div>
    </motion.div>
  )
}
