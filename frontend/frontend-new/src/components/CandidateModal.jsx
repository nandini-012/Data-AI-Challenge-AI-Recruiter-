import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MapPin, Briefcase, Clock, Star, Mail, Phone } from 'lucide-react'
import api from '../services/api'

export default function CandidateModal({ candidateId, onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!candidateId) return
    setLoading(true)
    setError(null)
    api
      .get(`/candidate/${candidateId}`)
      .then((res) => setData(res.data))
      .catch((err) =>
        setError(err.response?.data?.detail || 'Failed to load candidate')
      )
      .finally(() => setLoading(false))
  }, [candidateId])

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEsc)
    return () => document.removeEventListener('keydown', handleEsc)
  }, [onClose])

  if (!candidateId) return null

  const candidate = data?.candidate || {}
  const ranking = data?.ranking || null
  const profile = candidate.profile || {}
  const skills = candidate.skills || []
  const career = candidate.career_history || []
  const signals = candidate.redrob_signals || {}

  return (
    <AnimatePresence>
      <motion.div
        className="modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="modal-content"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>

          {loading ? (
            <div className="modal-loading">
              <div className="skeleton skeleton-lg" />
              <div className="skeleton skeleton-md" />
              <div className="skeleton skeleton-sm" />
              <div className="skeleton skeleton-md" />
            </div>
          ) : error ? (
            <div className="modal-error">{error}</div>
          ) : (
            <div className="modal-body">
              <div className="modal-header-section">
                <h2>{profile.current_title || 'Candidate'}</h2>
                <p className="modal-candidate-id">{candidate.candidate_id}</p>
                <div className="modal-meta">
                  {profile.current_company && (
                    <span>
                      <Briefcase size={14} /> {profile.current_company}
                    </span>
                  )}
                  {profile.location && (
                    <span>
                      <MapPin size={14} /> {profile.location}
                    </span>
                  )}
                  {profile.years_of_experience != null && (
                    <span>
                      <Clock size={14} /> {profile.years_of_experience} years exp.
                    </span>
                  )}
                </div>
              </div>

              {ranking && (
                <div className="modal-ranking-section">
                  <div className="ranking-badge">
                    <Star size={16} />
                    <span>Rank #{ranking.rank}</span>
                  </div>
                  <div className="ranking-score">
                    Score: {ranking.score?.toFixed(2)}
                  </div>
                  {ranking.reasoning && (
                    <p className="ranking-reasoning">{ranking.reasoning}</p>
                  )}
                </div>
              )}

              {skills.length > 0 && (
                <div className="modal-section">
                  <h3>Skills</h3>
                  <div className="skills-grid">
                    {skills.map((skill, i) => (
                      <span key={i} className="chip">
                        {skill.name}
                        {skill.proficiency && (
                          <span className="skill-level">{skill.proficiency}</span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {career.length > 0 && (
                <div className="modal-section">
                  <h3>Career History</h3>
                  <div className="career-timeline">
                    {career.map((job, i) => (
                      <div key={i} className="career-item">
                        <div className="career-dot" />
                        <div className="career-content">
                          <strong>{job.title || 'Role'}</strong>
                          {job.company && (
                            <span className="career-company">{job.company}</span>
                          )}
                          {job.duration && (
                            <span className="career-duration">{job.duration}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {signals && Object.keys(signals).length > 0 && (
                <div className="modal-section">
                  <h3>Signals</h3>
                  <div className="signals-grid">
                    {signals.open_to_work_flag && (
                      <span className="badge badge-success">
                        Open to Work
                      </span>
                    )}
                    {signals.verified_email && (
                      <span className="badge badge-success">
                        <Mail size={12} /> Verified Email
                      </span>
                    )}
                    {signals.verified_phone && (
                      <span className="badge badge-success">
                        <Phone size={12} /> Verified Phone
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
