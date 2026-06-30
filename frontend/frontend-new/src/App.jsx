import { lazy, Suspense, useState, useCallback } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import TopNavbar from './components/TopNavbar'
import CandidateModal from './components/CandidateModal'
import Toast from './components/Toast'
import { TableSkeleton } from './components/LoadingSkeleton'
import './App.css'

const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const RankingsPage = lazy(() => import('./pages/RankingsPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const JobDescriptionPage = lazy(() => import('./pages/JobDescriptionPage'))

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedCandidateId, setSelectedCandidateId] = useState(null)
  const [toast, setToast] = useState({ visible: false, message: '', type: 'success' })

  const showToast = useCallback((message, type = 'success') => {
    setToast({ visible: true, message, type })
  }, [])

  const closeToast = useCallback(() => {
    setToast(prev => ({ ...prev, visible: false }))
  }, [])

  return (
    <div className="app-layout">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        showToast={showToast}
      />
      <div className="main-wrapper">
        <TopNavbar
          onMenuToggle={() => setSidebarOpen(prev => !prev)}
          onSelectCandidate={setSelectedCandidateId}
        />
        <main className="main-content">
          <Suspense fallback={<TableSkeleton />}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/rankings" element={<RankingsPage onSelectCandidate={setSelectedCandidateId} />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/job-description" element={<JobDescriptionPage showToast={showToast} />} />
            </Routes>
          </Suspense>
        </main>
      </div>
      {selectedCandidateId && (
        <CandidateModal
          candidateId={selectedCandidateId}
          onClose={() => setSelectedCandidateId(null)}
        />
      )}
      <Toast
        message={toast.message}
        type={toast.type}
        visible={toast.visible}
        onClose={closeToast}
      />
    </div>
  )
}

export default App