import { useEffect, useState, useCallback } from 'react'
import api from '../api/client'
import Modal from './Modal'
import Badge from './Badge'
import styles from './EmployeeDrawer.module.css'

/**
 * Employee detail modal: profile, current assignments, and (when the
 * employee has headroom) recommended at-risk projects with one-click assign.
 * Reusable from any page: <EmployeeDrawer employeeId={id} onClose={fn} onChanged={fn} />
 * onChanged fires after a successful assignment so the parent can refetch.
 */
export default function EmployeeDrawer({ employeeId, onClose, onChanged }) {
  const [detail, setDetail] = useState(null)
  const [recs, setRecs]     = useState(null)
  const [pct, setPct]       = useState(50)
  const [busy, setBusy]     = useState(null)   // project_id being assigned
  const [notice, setNotice] = useState(null)
  const [error, setError]   = useState(null)

  const load = useCallback(() => {
    api.get(`/api/employees/${employeeId}/detail`).then(r => setDetail(r.data))
    api.get(`/api/employees/${employeeId}/recommendations`).then(r => {
      setRecs(r.data)
      setPct(p => Math.min(p, Math.max(5, Math.floor(r.data.headroom))))
    })
  }, [employeeId])

  useEffect(() => { load() }, [load])

  const assign = async (project) => {
    setBusy(project.project_id)
    setError(null)
    try {
      const r = await api.post(`/api/employees/${employeeId}/assign`, {
        project_id: project.project_id,
        allocation_pct: pct,
      })
      const { project: p, allocated_pct } = r.data
      setNotice(
        `Assigned at ${allocated_pct}% to ${project.project_name}. ` +
        (p.previous_rag !== p.rag_status
          ? `Project moved ${p.previous_rag} → ${p.rag_status}.`
          : `Project backlog reduced (${p.overdue_tasks} overdue left).`)
      )
      load()
      onChanged?.()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setBusy(null)
    }
  }

  if (!detail) {
    return (
      <Modal title="Employee" onClose={onClose} wide>
        <p className={styles.loading}>Loading…</p>
      </Modal>
    )
  }

  const e = detail.employee
  const showRecs = recs && recs.headroom > 0 && recs.projects.length > 0

  return (
    <Modal title={e.full_name} onClose={onClose} wide>
      <div className={styles.topRow}>
        <div className={styles.infoGrid}>
          <Info label="Designation" value={e.designation} />
          <Info label="Department" value={e.department} />
          <Info label="Practice" value={e.practice_area} />
          <Info label="Location" value={e.location} />
          <Info label="Manager" value={e.reporting_manager} />
          <Info label="Email" value={e.email} />
        </div>
        <div className={styles.utilBox}>
          <span className={styles.utilPct}>{e.total_allocation_pct}%</span>
          <Badge value={e.utilization_status} />
        </div>
      </div>

      {Array.isArray(e.skills) && e.skills.length > 0 && (
        <div className={styles.skills}>
          {e.skills.map(s => <span key={s} className={styles.skillChip}>{s}</span>)}
        </div>
      )}

      <h3 className={styles.sectionHead}>Current Assignments</h3>
      {detail.allocations.length === 0 ? (
        <p className={styles.emptyText}>No active project assignments.</p>
      ) : (
        <div className={styles.allocList}>
          {detail.allocations.map(a => (
            <div key={a.project_id} className={styles.allocRow}>
              <div className={styles.allocMain}>
                <span className={styles.allocName}>{a.project_name}</span>
                <span className={styles.allocSub}>{a.client_name} · {a.role_on_project}</span>
              </div>
              <Badge value={a.rag_status} />
              <span className={styles.allocPct}>{a.allocation_pct}%</span>
            </div>
          ))}
        </div>
      )}

      {notice && <p className={styles.notice}>{notice}</p>}
      {error && <p className={styles.error}>{error}</p>}

      {showRecs && (
        <>
          <div className={styles.recHead}>
            <h3 className={styles.sectionHead}>
              Recommended Projects
              <span className={styles.headroom}>{Math.floor(recs.headroom)}% headroom</span>
            </h3>
            <label className={styles.pctLabel}>
              Assign at
              <select
                className={styles.pctSelect}
                value={pct}
                onChange={ev => setPct(Number(ev.target.value))}
              >
                {[25, 50, 75, 100]
                  .filter(v => v <= recs.headroom)
                  .map(v => <option key={v} value={v}>{v}%</option>)}
              </select>
            </label>
          </div>
          <div className={styles.recList}>
            {recs.projects.map(p => (
              <div key={p.project_id} className={styles.recRow}>
                <div className={styles.allocMain}>
                  <span className={styles.allocName}>{p.project_name}</span>
                  <span className={styles.allocSub}>{p.client_name} · PM: {p.project_manager}</span>
                  <span className={styles.recReason}>{p.reason}</span>
                </div>
                <button
                  className={styles.assignBtn}
                  disabled={busy !== null}
                  onClick={() => assign(p)}
                >
                  {busy === p.project_id ? 'Assigning…' : 'Assign'}
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </Modal>
  )
}

function Info({ label, value }) {
  return (
    <div className={styles.info}>
      <span className={styles.infoLabel}>{label}</span>
      <span className={styles.infoValue}>{value || '—'}</span>
    </div>
  )
}
