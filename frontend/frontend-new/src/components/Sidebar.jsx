import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Trophy, BarChart3, FileText, Download, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/rankings', icon: Trophy, label: 'Rankings' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/job-description', icon: FileText, label: 'Job Description' },
]

export default function Sidebar({ isOpen, onClose, showToast }) {
  const handleDownload = async () => {
    try {
      const res = await api.get('/rank/download', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = 'submission.csv'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      showToast?.('CSV downloaded successfully')
    } catch (err) {
      console.error('Download failed:', err)
      showToast?.('Download failed. Please try again.', 'error')
    }
  }

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="sidebar-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
        )}
      </AnimatePresence>
      <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">AI</div>
            <span className="sidebar-logo-text">Recruiter</span>
          </div>
          <button className="sidebar-close-btn" onClick={onClose} aria-label="Close sidebar">
            <X size={20} />
          </button>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link--active' : ''}`
              }
              onClick={onClose}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button className="sidebar-download-btn" onClick={handleDownload}>
            <Download size={18} />
            <span>Download CSV</span>
          </button>
        </div>
      </aside>
    </>
  )
}
