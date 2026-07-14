import { useEffect, useState } from 'react'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const COLUMNS = [
  { key: 'full_name',              label: 'Employee' },
  { key: 'designation',            label: 'Role' },
  { key: 'department',             label: 'Dept' },
  { key: 'joining_date',           label: 'Joined' },
  { key: 'checklist_pct',          label: 'Checklist %', render: v => `${v}%` },
  { key: 'status',                 label: 'Status' },
  { key: 'laptop_issued',          label: 'Laptop', render: v => v ? 'Done' : 'Pending' },
  { key: 'induction_done',         label: 'Induction', render: v => v ? 'Done' : 'Pending' },
  { key: 'first_project_assigned', label: 'Project', render: v => v ? 'Assigned' : 'Pending' },
  { key: 'onboarding_score',       label: 'Score' },
  { key: 'assigned_buddy',         label: 'Buddy' },
]

const STATUS_OPTIONS = ['All', 'Completed', 'In Progress']

export default function PeopleOps() {
  const [data, setData]       = useState([])
  const [summary, setSummary] = useState(null)
  const [status, setStatus]   = useState('All')
  const [detail, setDetail]   = useState(null)

  useEffect(() => {
    api.get('/api/onboarding').then(r => setData(r.data))
    api.get('/api/onboarding/summary').then(r => setSummary(r.data))
  }, [])

  const filtered = status === 'All' ? data : data.filter(r => r.status === status)

  return (
    <PageShell title="People Operations" subtitle="New joiner onboarding tracker and checklist completion">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Total Joiners"    value={summary.total} />
          <KPICard label="Completed"        value={summary.completed}       accent="#1a7a4a" />
          <KPICard label="In Progress"      value={summary.in_progress}     accent="#b7690a" />
          <KPICard label="Needs Attention"  value={summary.needs_attention} accent="#c0392b" sub="checklist < 60%" />
          <KPICard label="Avg Completion"   value={`${summary.avg_completion}%`} />
          <KPICard label="Avg Score"        value={summary.avg_score} sub="out of 5" />
        </div>
      )}
      <div className={styles.filters}>
        <span className={styles.filterLabel}>Status</span>
        {STATUS_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${status === o ? styles.active : ''}`} onClick={() => setStatus(o)}>{o}</button>
        ))}
      </div>
      <DataTable data={filtered} columns={COLUMNS} onRowClick={setDetail} />
      {detail && (
        <RecordDetail
          title={`${detail.full_name} — onboarding`}
          record={detail}
          onClose={() => setDetail(null)}
        />
      )}
    </PageShell>
  )
}
