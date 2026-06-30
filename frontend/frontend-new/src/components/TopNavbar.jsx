import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Menu } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import api from '../services/api'

export default function TopNavbar({ onMenuToggle, onSelectCandidate }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const timeoutRef = useRef(null)
  const dropdownRef = useRef(null)

  useEffect(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    const trimmed = query.trim()
    if (!trimmed) {
      setResults([])
      setShowDropdown(false)
      return
    }
    timeoutRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await api.get('/search', { params: { q: trimmed, limit: 6 } })
        setResults(res.data.candidates || [])
        setShowDropdown(true)
      } catch (err) {
        console.error('Search error:', err)
      } finally {
        setLoading(false)
      }
    }, 300)
    return () => clearTimeout(timeoutRef.current)
  }, [query])

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && query.trim()) {
      setShowDropdown(false)
      navigate(`/rankings?q=${encodeURIComponent(query.trim())}`)
    }
  }

  const handleSelectCandidate = (candidateId) => {
    setShowDropdown(false)
    setQuery('')
    onSelectCandidate(candidateId)
  }

  return (
    <header className="topbar">
      <button className="topbar-menu-btn" onClick={onMenuToggle} aria-label="Toggle menu">
        <Menu size={20} />
      </button>
      <div className="search-container" ref={dropdownRef}>
        <Search size={18} className="search-icon" />
        <input
          type="text"
          className="search-input"
          placeholder="Search candidates by skill, role, or ID..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setShowDropdown(true)}
          id="global-search"
        />
        <AnimatePresence>
          {showDropdown && (
            <motion.div
              className="search-dropdown"
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
            >
              {loading ? (
                <div className="search-dropdown-loading">Searching…</div>
              ) : results.length > 0 ? (
                <>
                  {results.map((c) => (
                    <button
                      key={c.candidate_id}
                      className="search-result"
                      onClick={() => handleSelectCandidate(c.candidate_id)}
                    >
                      <div className="search-result-title">
                        {c.current_title || 'Untitled'}
                      </div>
                      <div className="search-result-meta">
                        {c.candidate_id}
                        {c.years_of_experience != null && ` · ${c.years_of_experience}y exp`}
                        {c.score != null && ` · Score: ${c.score.toFixed(2)}`}
                      </div>
                    </button>
                  ))}
                  <button
                    className="search-view-all"
                    onClick={() => {
                      setShowDropdown(false)
                      navigate(`/rankings?q=${encodeURIComponent(query.trim())}`)
                    }}
                  >
                    View all results →
                  </button>
                </>
              ) : (
                <div className="search-dropdown-empty">No results found</div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  )
}
