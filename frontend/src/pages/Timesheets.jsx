import { useEffect, useState } from 'react'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const COLUMNS = [
  { key: 'full_name',        label: 'Employee' },
  { key: 'department',       label: 'Dept' },
  { key: 'week_ending_date', label: 'Week Ending' },
  { key: 'task_type',        label: 'Task Type' },
  { key: 'hours_logged',     label: 'Hours', render: v => `${v}h` },
  { key: 'is_billable',      label: 'Billable', render: v => v ? 'Yes' : 'No' },
  { key: 'submission_status',label: 'Submission' },
  { key: 'approval_status',  label: 'Approval' },
]

const SUB_OPTIONS  = ['All', 'On Time', 'Late']
const APPR_OPTIONS = ['All', 'Approved', 'Pending']

export default function Timesheets() {
  const [data, setData]       = useState([])
  const [summary, setSummary] = useState(null)
  const [sub, setSub]         = useState('All')
  const [appr, setAppr]       = useState('All')
  const [detail, setDetail]   = useState(null)

  useEffect(() => {
    api.get('/api/timesheets').then(r => setData(r.data))
    api.get('/api/timesheets/summary').then(r => setSummary(r.data))
  }, [])

  const filtered = data
    .filter(r => sub === 'All'  || r.submission_status === sub)
    .filter(r => appr === 'All' || r.approval_status === appr)

  return (
    <PageShell title="Timesheets" subtitle="Submission compliance and billable hours tracking">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Total Entries"   value={summary.total_entries} />
          <KPICard label="On Time"         value={summary.on_time}       accent="#1a7a4a" />
          <KPICard label="Late"            value={summary.late}          accent="#c0392b" />
          <KPICard label="Approved"        value={summary.approved}      accent="#1a7a4a" />
          <KPICard label="Pending"         value={summary.pending}       accent="#b7690a" />
          <KPICard label="Compliance Rate" value={`${summary.compliance_pct}%`} />
        </div>
      )}
      <div className={styles.filters}>
        <span className={styles.filterLabel}>Submission</span>
        {SUB_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${sub === o ? styles.active : ''}`} onClick={() => setSub(o)}>{o}</button>
        ))}
        <span className={styles.filterLabel} style={{ marginLeft: 12 }}>Approval</span>
        {APPR_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${appr === o ? styles.active : ''}`} onClick={() => setAppr(o)}>{o}</button>
        ))}
      </div>
      <DataTable data={filtered} columns={COLUMNS} onRowClick={setDetail} />
      {detail && (
        <RecordDetail
          title={`${detail.full_name} — week of ${detail.week_ending_date}`}
          record={detail}
          onClose={() => setDetail(null)}
        />
      )}
    </PageShell>
  )
}
