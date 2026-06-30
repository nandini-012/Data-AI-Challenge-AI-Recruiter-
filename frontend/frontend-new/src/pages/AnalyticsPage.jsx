import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { Users, Shield, Activity } from 'lucide-react'
import StatCard from '../components/StatCard'
import { CardSkeleton, ChartSkeleton } from '../components/LoadingSkeleton'
import ErrorState from '../components/ErrorState'
import api from '../services/api'

const COLORS = [
  '#8C6A40',
  '#A0876A',
  '#60A5FA',
  '#4ADE80',
  '#FBBF24',
  '#9AA0A6',
  '#818CF8',
  '#FB923C',
  '#34D399',
  '#F87171',
]

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      <p className="chart-tooltip-value">
        {payload[0].value?.toLocaleString()}
      </p>
    </div>
  )
}

export default function AnalyticsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAnalytics = () => {
    setLoading(true)
    setError(null)
    api
      .get('/analytics')
      .then((res) => setData(res.data))
      .catch((err) =>
        setError(err.response?.data?.detail || err.message)
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchAnalytics()
  }, [])

  if (loading)
    return (
      <div className="page-container">
        <CardSkeleton count={3} />
        <div style={{ marginTop: 24 }}>
          <ChartSkeleton />
        </div>
      </div>
    )
  if (error) return <ErrorState message={error} onRetry={fetchAnalytics} />

  const stats = data.behavior_statistics || {}

  return (
    <div className="page-container">
      <motion.h1
        className="page-title"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        Analytics
      </motion.h1>

      <div className="stats-grid stats-grid--3">
        <StatCard
          icon={Users}
          label="Open to Work"
          value={stats.open_to_work_candidates?.toLocaleString()}
          color="#4ADE80"
          delay={0}
        />
        <StatCard
          icon={Shield}
          label="Verified Email"
          value={stats.verified_email_candidates?.toLocaleString()}
          color="#60A5FA"
          delay={0.1}
        />
        <StatCard
          icon={Activity}
          label="Avg Response Rate"
          value={
            stats.average_recruiter_response_rate != null
              ? `${(stats.average_recruiter_response_rate * 100).toFixed(1)}%`
              : '—'
          }
          color="#FBBF24"
          delay={0.2}
        />
      </div>

      <div className="analytics-charts">
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="card-title">Experience Distribution</h2>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.experience_distribution}>
                <XAxis dataKey="range" stroke="#6B7280" fontSize={12} />
                <YAxis stroke="#6B7280" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {data.experience_distribution?.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="card-title">Top Skills</h2>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={data.skill_frequency?.slice(0, 12)}
                layout="vertical"
                margin={{ left: 20 }}
              >
                <XAxis type="number" stroke="#6B7280" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#6B7280"
                  fontSize={11}
                  width={100}
                  tick={{ fill: '#9AA0A6' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {data.skill_frequency?.slice(0, 12).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="card-title">Role Distribution</h2>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={data.role_distribution?.slice(0, 10)}
                layout="vertical"
                margin={{ left: 20 }}
              >
                <XAxis type="number" stroke="#6B7280" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#6B7280"
                  fontSize={11}
                  width={130}
                  tick={{ fill: '#9AA0A6' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {data.role_distribution?.slice(0, 10).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h2 className="card-title">Behavioral Statistics</h2>
          <div className="behavior-stats-grid">
            <div className="behavior-stat">
              <span className="behavior-stat-value">
                {stats.verified_phone_candidates?.toLocaleString()}
              </span>
              <span className="behavior-stat-label">Verified Phone</span>
            </div>
            <div className="behavior-stat">
              <span className="behavior-stat-value">
                {stats.average_response_time_hours?.toFixed(1)}h
              </span>
              <span className="behavior-stat-label">
                Avg Response Time
              </span>
            </div>
            <div className="behavior-stat">
              <span className="behavior-stat-value">
                {stats.average_interview_completion_rate != null
                  ? `${(stats.average_interview_completion_rate * 100).toFixed(1)}%`
                  : '—'}
              </span>
              <span className="behavior-stat-label">
                Interview Completion
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
