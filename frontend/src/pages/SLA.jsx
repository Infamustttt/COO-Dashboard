import { useEffect, useState } from 'react'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const COLUMNS = [
  { key: 'sla_id',           label: 'SLA ID' },
  { key: 'client_name',      label: 'Client' },
  { key: 'sla_type',         label: 'Type' },
  { key: 'target_value',     label: 'Target' },
  { key: 'actual_value',     label: 'Actual' },
  { key: 'compliance_status',label: 'Status' },
  { key: 'breach_count',     label: 'Breaches' },
  { key: 'has_penalty',      label: 'Penalty?', render: v => v ? 'Yes' : 'No' },
  { key: 'penalty_amount',   label: 'Penalty $', render: v => v ? `$${Number(v).toLocaleString()}` : '—' },
  { key: 'assigned_owner',   label: 'Owner' },
]

const STATUS_OPTIONS = ['All', 'Met', 'Breached']
const TYPE_OPTIONS   = ['All', 'Uptime', 'Response Time', 'Resolution Time', 'Delivery']

export default function SLA() {
  const [data, setData]       = useState([])
  const [summary, setSummary] = useState(null)
  const [status, setStatus]   = useState('All')
  const [type, setType]       = useState('All')
  const [detail, setDetail]   = useState(null)

  useEffect(() => {
    api.get('/api/slas').then(r => setData(r.data))
    api.get('/api/slas/summary').then(r => setSummary(r.data))
  }, [])

  const filtered = data
    .filter(r => status === 'All' || r.compliance_status === status)
    .filter(r => type === 'All' || r.sla_type === type)

  return (
    <PageShell title="SLA Compliance" subtitle="Service level agreement tracking per client and type">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Total SLAs"       value={summary.total} />
          <KPICard label="Met"              value={summary.met}             accent="#1a7a4a" />
          <KPICard label="Breached"         value={summary.breached}        accent="#c0392b" />
          <KPICard label="Compliance Rate"  value={`${summary.compliance_pct}%`} />
          <KPICard label="Penalty Exposure" value={summary.total_penalty_exposure
            ? `$${Number(summary.total_penalty_exposure).toLocaleString()}`
            : '$0'} accent="#b7690a" />
        </div>
      )}
      <div className={styles.filters}>
        <span className={styles.filterLabel}>Status</span>
        {STATUS_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${status === o ? styles.active : ''}`} onClick={() => setStatus(o)}>{o}</button>
        ))}
        <span className={styles.filterLabel} style={{ marginLeft: 12 }}>Type</span>
        {TYPE_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${type === o ? styles.active : ''}`} onClick={() => setType(o)}>{o}</button>
        ))}
      </div>
      <DataTable data={filtered} columns={COLUMNS} onRowClick={setDetail} />
      {detail && (
        <RecordDetail
          title={`${detail.sla_id} — ${detail.client_name}`}
          record={detail}
          onClose={() => setDetail(null)}
        />
      )}
    </PageShell>
  )
}
