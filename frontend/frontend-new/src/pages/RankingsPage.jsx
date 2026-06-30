import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Hash, User, Star, Briefcase, Clock, Eye } from 'lucide-react'
import Pagination from '../components/Pagination'
import { TableSkeleton } from '../components/LoadingSkeleton'
import ErrorState from '../components/ErrorState'
import api from '../services/api'

const getMatchSummary = (reasoning) => {
  if (!reasoning) return '—'
  const words = reasoning.split(/\s+/)
  if (words.length <= 10) return reasoning
  return words.slice(0, 10).join(' ') + '…'
}

export default function RankingsPage({ onSelectCandidate }) {
  const [searchParams] = useSearchParams()
  const queryParam = searchParams.get('q') || ''
  const [data, setData] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const isSearchMode = queryParam.trim().length > 0

  const fetchData = () => {
    setLoading(true)
    setError(null)
    const endpoint = isSearchMode ? '/search' : '/rank'
    const currentJD = localStorage.getItem("currentJD") || ""
    const params = isSearchMode
  ? { q: queryParam, jd: currentJD, page, limit: 20 }
  : {
      jd: currentJD,
      page,
      limit: 20,
    }
    api
      .get(endpoint, { params })
      .then((res) => setData(res.data))
      .catch((err) =>
        setError(err.response?.data?.detail || err.message)
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    setPage(1)
  }, [queryParam])

  useEffect(() => {
    fetchData()
  }, [page, queryParam])

  const handlePageChange = (newPage) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (error) return <ErrorState message={error} onRetry={fetchData} />

  return (
    <div className="page-container">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <h1 className="page-title">
          {isSearchMode ? 'Search Results' : 'Candidate Rankings'}
        </h1>
        {isSearchMode && (
          <p className="page-subtitle">
            Showing results for "<strong>{queryParam}</strong>"
            {data && ` — ${data.total?.toLocaleString()} matches`}
          </p>
        )}
        {!isSearchMode && data && (
          <p className="page-subtitle">
            {data.total?.toLocaleString()} ranked candidates
          </p>
        )}
      </motion.div>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : (
        <motion.div
          className="card table-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>
                    <Hash size={14} /> Rank
                  </th>
                  <th>
                    <User size={14} /> Candidate
                  </th>
                  <th>
                    <Clock size={14} /> Experience
                  </th>
                  <th>
                    <Star size={14} /> Score
                  </th>
                  <th>
                    AI Summary
                  </th>
                  <th>
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {data?.candidates?.map((c, i) => (
                  <motion.tr
                    key={c.candidate_id}
                    className="table-row"
                    onClick={() => onSelectCandidate(c.candidate_id)}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.02 }}
                  >
                    <td>
                      <span className="rank-badge">
                        #{c.rank ?? '—'}
                      </span>
                    </td>
                    <td className="candidate-id-cell">
                      {c.candidate_id}
                    </td>
                    <td>
                      {c.years_of_experience != null
                        ? `${c.years_of_experience}y`
                        : '—'}
                    </td>
                    <td>
                      <span className="score-value">
                        {c.score != null ? c.score.toFixed(2) : '—'}
                      </span>
                    </td>
                    <td className="ai-summary">
                      {getMatchSummary(c.reasoning)}
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          onSelectCandidate(c.candidate_id)
                        }}
                        aria-label="View profile"
                      >
                        <Eye size={15} />
                        <span>View</span>
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          {data?.candidates?.length === 0 && (
            <div className="empty-state">
              <Search size={48} />
              <p>No candidates found</p>
            </div>
          )}
        </motion.div>
      )}

      {data && (
        <Pagination
          page={data.page}
          totalPages={data.total_pages}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  )
}
