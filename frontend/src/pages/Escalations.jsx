import { useEffect, useState } from 'react'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const shortDate = v => (v ? String(v).slice(0, 10) : '—')

const COLUMNS = [
  { key: 'severity',         label: 'Sev' },
  { key: 'title',            label: 'Title' },
  { key: 'escalation_type',  label: 'Type' },
  { key: 'status',           label: 'Status' },
  { key: 'days_open',        label: 'Days' },
  { key: 'assigned_owner',   label: 'Owner' },
  { key: 'raised_by',        label: 'Raised By' },
  { key: 'raised_date',      label: 'Raised',      render: shortDate },
  { key: 'resolution_target',label: 'Target',      render: shortDate },
]

const SEV_OPTIONS  = ['All', 'P1', 'P2', 'P3']
const STAT_OPTIONS = ['All', 'Open', 'In Progress', 'Resolved']
const TYPE_OPTIONS = ['All', 'SLA Breach', 'Delivery Risk', 'People', 'Financial']

export default function Escalations() {
  const [data, setData]       = useState([])
  const [summary, setSummary] = useState(null)
  const [sev, setSev]         = useState('All')
  const [stat, setStat]       = useState('All')
  const [type, setType]       = useState('All')
  const [detail, setDetail]   = useState(null)

  useEffect(() => {
    api.get('/api/escalations').then(r => setData(r.data))
    api.get('/api/escalations/summary').then(r => setSummary(r.data))
  }, [])

  const filtered = data
    .filter(r => sev === 'All'  || r.severity === sev)
    .filter(r => stat === 'All' || r.status === stat)
    .filter(r => type === 'All' || r.escalation_type === type)

  return (
    <PageShell title="Escalations" subtitle="Open issues by severity and type">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Open Total"   value={summary.open_total} />
          <KPICard label="P1 Open"      value={summary.p1_open}   accent="#c0392b" />
          <KPICard label="P2 Open"      value={summary.p2_open}   accent="#b7690a" />
          <KPICard label="P3 Open"      value={summary.p3_open}   accent="#3a5ba0" />
          <KPICard label="Resolved"     value={summary.resolved}  accent="#1a7a4a" />
          <KPICard label="Avg Days Open"value={summary.avg_days_open} />
        </div>
      )}
      <div className={styles.filters}>
        <span className={styles.filterLabel}>Severity</span>
        {SEV_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${sev === o ? styles.active : ''}`} onClick={() => setSev(o)}>{o}</button>
        ))}
        <span className={styles.filterLabel} style={{ marginLeft: 12 }}>Status</span>
        {STAT_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${stat === o ? styles.active : ''}`} onClick={() => setStat(o)}>{o}</button>
        ))}
        <span className={styles.filterLabel} style={{ marginLeft: 12 }}>Type</span>
        {TYPE_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${type === o ? styles.active : ''}`} onClick={() => setType(o)}>{o}</button>
        ))}
      </div>
      <DataTable data={filtered} columns={COLUMNS} onRowClick={setDetail} />
      {detail && (
        <RecordDetail
          title={detail.title}
          record={detail}
          onClose={() => setDetail(null)}
        />
      )}
    </PageShell>
  )
}
