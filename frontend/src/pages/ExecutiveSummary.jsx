import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import styles from './ExecutiveSummary.module.css'

const BRIEFING_KEY = 'coo_briefing_cache'

function loadCachedBriefing() {
  try {
    const raw = sessionStorage.getItem(BRIEFING_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export default function ExecutiveSummary() {
  const navigate = useNavigate()
  const [summary, setSummary]     = useState(null)
  const [briefing, setBriefing]   = useState(loadCachedBriefing)
  const [briefError, setBriefError] = useState(null)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    Promise.all([
      api.get('/api/projects/summary'),
      api.get('/api/employees/summary'),
      api.get('/api/slas/summary'),
      api.get('/api/escalations/summary'),
      api.get('/api/csat/summary'),
    ]).then(([p, e, s, esc, c]) => {
      setSummary({ projects: p.data, employees: e.data, slas: s.data, escalations: esc.data, csat: c.data })
    })
  }, [])

  const generateBriefing = async () => {
    setGenerating(true)
    setBriefError(null)
    try {
      const r = await api.get('/api/briefing')
      setBriefing(r.data.briefing)
      try { sessionStorage.setItem(BRIEFING_KEY, JSON.stringify(r.data.briefing)) } catch {}
    } catch (err) {
      console.error('Briefing failed:', err)
      setBriefing(null)
      setBriefError(err.response?.data?.detail || err.message)
    } finally {
      setGenerating(false)
    }
  }

  if (!summary) return <div className={styles.loading}>Loading...</div>

  const { projects: p, employees: e, slas: s, escalations: esc, csat: c } = summary

  return (
    <PageShell title="Executive Summary" subtitle="Live operational snapshot">
      <div className={styles.kpiGrid}>
        <KPICard label="Total Projects"   value={p.total} />
        <KPICard label="Red Projects"     value={p.red}   accent="#c0392b" />
        <KPICard label="Amber Projects"   value={p.amber} accent="#b7690a" />
        <KPICard label="Avg Completion"   value={`${p.avg_completion}%`} />
        <KPICard label="Active Employees" value={e.active} />
        <KPICard label="On Bench"         value={e.bench} accent="#b7690a" />
        <KPICard label="Over-allocated"   value={e.over_allocated} accent="#c0392b" />
        <KPICard label="Avg Utilisation"  value={`${e.avg_allocation}%`} />
        <KPICard label="SLA Compliance"   value={`${s.compliance_pct}%`} sub={`${s.breached} breached`} />
        <KPICard label="Avg CSAT Score"   value={c.avg_score} sub="out of 5" />
        <KPICard label="Open Escalations" value={esc.open_total} />
        <KPICard label="P1 Escalations"   value={esc.p1_open} accent="#c0392b" />
      </div>

      <div className={styles.briefingSection}>
        <div className={styles.briefingHeader}>
          <h2 className={styles.sectionTitle}>Weekly AI Briefing</h2>
          <button
            className={styles.generateBtn}
            onClick={generateBriefing}
            disabled={generating}
          >
            {generating ? 'Generating...' : briefing ? 'Regenerate Briefing' : 'Generate Briefing'}
          </button>
        </div>
        {briefError && (
          <div className={styles.briefingCard}>
            <p className={styles.briefingText}>Could not generate briefing: {briefError}</p>
          </div>
        )}
        {briefing && (
          <>
            <div className={styles.briefingCard}>
              <p className={styles.briefingText}>
                {typeof briefing === 'string' ? briefing : briefing.summary}
              </p>
            </div>
            {briefing.emergencies?.map((em, i) => (
              <div key={i} className={styles.emergencyCard}>
                <div className={styles.emergencyBody}>
                  <h3 className={styles.emergencyTitle}>
                    <span className={styles.emergencyRank}>{i + 1}</span>
                    {em.title}
                  </h3>
                  <ul className={styles.emergencyPoints}>
                    {em.points?.map((pt, j) => <li key={j}>{pt}</li>)}
                  </ul>
                  {em.action && (
                    <p className={styles.emergencyAction}>
                      <strong>Recommended action:</strong> {em.action}
                    </p>
                  )}
                </div>
                <button
                  className={styles.resolveBtn}
                  onClick={() => navigate(`/${em.page}`)}
                >
                  {em.page_label || 'Investigate'} →
                </button>
              </div>
            ))}
          </>
        )}
      </div>
    </PageShell>
  )
}
