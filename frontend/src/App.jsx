import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import ExecutiveSummary from './pages/ExecutiveSummary'
import Projects from './pages/Projects'
import Resources from './pages/Resources'
import SLA from './pages/SLA'
import CSAT from './pages/CSAT'
import Escalations from './pages/Escalations'
import Timesheets from './pages/Timesheets'
import PeopleOps from './pages/PeopleOps'
import SOPs from './pages/SOPs'
import styles from './App.module.css'

function Guard({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className={styles.loading}>Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

function Layout() {
  return (
    <>
      <Navbar />
      <main className={styles.main}>
        <Routes>
          <Route path="/"            element={<ExecutiveSummary />} />
          <Route path="/projects"    element={<Projects />} />
          <Route path="/resources"   element={<Resources />} />
          <Route path="/sla"         element={<SLA />} />
          <Route path="/csat"        element={<CSAT />} />
          <Route path="/escalations" element={<Escalations />} />
          <Route path="/timesheets"  element={<Timesheets />} />
          <Route path="/people"      element={<PeopleOps />} />
          <Route path="/sops"        element={<SOPs />} />
          <Route path="*"            element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*"     element={<Guard><Layout /></Guard>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
