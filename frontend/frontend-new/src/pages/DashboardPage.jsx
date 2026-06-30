import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Users, UserCheck, Clock, Star, Zap, TrendingUp } from 'lucide-react'
import StatCard from '../components/StatCard'
import { CardSkeleton } from '../components/LoadingSkeleton'
import ErrorState from '../components/ErrorState'
import api from '../services/api'

export default function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDashboard = () => {
    setLoading(true)
    setError(null)
    api
      .get('/dashboard', {
        params: { jd: localStorage.getItem('currentJD') || '' },
      })
      .then((res) => setData(res.data))
      .catch((err) =>
        setError(err.response?.data?.detail || err.message)
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchDashboard()
  }, [])

  if (loading) return <CardSkeleton count={4} />
  if (error) return <ErrorState message={error} onRetry={fetchDashboard} />

  return (
    <div className="page-container">
      <motion.h1
        className="page-title"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        Dashboard
      </motion.h1>

      <div className="stats-grid">
        <StatCard
          icon={Users}
          label="Total Candidates"
          value={data.total_candidates?.toLocaleString()}
          delay={0}
          color="#60A5FA"
        />
        <StatCard
          icon={UserCheck}
          label="Shortlisted"
          value={data.shortlisted_candidates?.toLocaleString()}
          delay={0.1}
          color="#4ADE80"
        />
        <StatCard
          icon={Clock}
          label="Avg Experience"
          value={`${data.average_experience} yrs`}
          delay={0.2}
          color="#FBBF24"
        />
        <StatCard
          icon={Star}
          label="Avg Score"
          value={data.average_score?.toFixed(2)}
          delay={0.3}
          color="#8C6A40"
        />
      </div>

      <div className="dashboard-charts">
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="card-title">
            <Zap size={20} /> Top Skills
          </h2>
          <div className="bar-chart-list">
            {data.most_common_skills?.map((skill, i) => {
              const max = data.most_common_skills[0]?.count || 1
              return (
                <div key={skill.name} className="bar-chart-item">
                  <span className="bar-label">{skill.name}</span>
                  <div className="bar-track">
                    <motion.div
                      className="bar-fill"
                      initial={{ width: 0 }}
                      animate={{
                        width: `${(skill.count / max) * 100}%`,
                      }}
                      transition={{
                        delay: 0.5 + i * 0.05,
                        duration: 0.6,
                      }}
                    />
                  </div>
                  <span className="bar-value">
                    {skill.count.toLocaleString()}
                  </span>
                </div>
              )
            })}
          </div>
        </motion.div>

        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="card-title">
            <TrendingUp size={20} /> Role Distribution
          </h2>
          <div className="bar-chart-list">
            {data.role_distribution?.map((role, i) => {
              const max = data.role_distribution[0]?.count || 1
              return (
                <div key={role.name} className="bar-chart-item">
                  <span className="bar-label">{role.name}</span>
                  <div className="bar-track">
                    <motion.div
                      className="bar-fill bar-fill--alt"
                      initial={{ width: 0 }}
                      animate={{
                        width: `${(role.count / max) * 100}%`,
                      }}
                      transition={{
                        delay: 0.6 + i * 0.05,
                        duration: 0.6,
                      }}
                    />
                  </div>
                  <span className="bar-value">
                    {role.count.toLocaleString()}
                  </span>
                </div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
