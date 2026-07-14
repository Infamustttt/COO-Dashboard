import { useEffect, useState } from 'react'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import EmailComposer from '../components/EmailComposer'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const RAG_OPTIONS = ['All', 'RED', 'AMBER', 'GREEN']

function buildEmailDraft(p) {
  const subject = `[${p.rag_status}] ${p.project_name} — status review required`
  const body =
`Hi ${p.project_manager.split(' ')[0]},

${p.project_name} (${p.project_id}) for ${p.client_name} is currently flagged ${p.rag_status}.

Current position:
- Completion: ${p.completion_pct}%
- Budget consumed: ${p.budget_consumed_pct}%
- Overdue tasks: ${p.overdue_tasks}
- Open issues: ${p.open_issues}

Please share a recovery plan and updated timeline by end of week. Flag any blockers or resourcing needs you want escalated.

Regards,`
  return { to: p.pm_email, subject, body }
}

export default function Projects() {
  const [data, setData]         = useState([])
  const [summary, setSummary]   = useState(null)
  const [rag, setRag]           = useState('All')
  const [composer, setComposer] = useState(null)   // project being emailed
  const [detail, setDetail]     = useState(null)

  useEffect(() => {
    api.get('/api/projects').then(r => setData(r.data))
    api.get('/api/projects/summary').then(r => setSummary(r.data))
  }, [])

  const columns = [
    { key: 'project_id',         label: 'ID' },
    { key: 'project_name',       label: 'Project' },
    { key: 'client_name',        label: 'Client' },
    { key: 'rag_status',         label: 'RAG' },
    { key: 'current_phase',      label: 'Phase' },
    { key: 'completion_pct',     label: 'Completion %', render: v => `${v}%` },
    { key: 'budget_consumed_pct',label: 'Budget Used %', render: v => `${v}%` },
    { key: 'overdue_tasks',      label: 'Overdue' },
    { key: 'open_issues',        label: 'Issues' },
    { key: 'project_manager',    label: 'PM' },
    {
      key: 'pm_email',
      label: '',
      render: (_, row) => (
        <button
          className={styles.rowActionBtn}
          onClick={e => { e.stopPropagation(); setComposer(row) }}
          title={`Email ${row.project_manager}`}
        >
          ✉ Email PM
        </button>
      ),
    },
  ]

  const filtered = rag === 'All' ? data : data.filter(r => r.rag_status === rag)

  return (
    <PageShell title="Project Delivery" subtitle="RAG status, budget and delivery tracking">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Total Projects"  value={summary.total} />
          <KPICard label="Red"             value={summary.red}   accent="#c0392b" />
          <KPICard label="Amber"           value={summary.amber} accent="#b7690a" />
          <KPICard label="Green"           value={summary.green} accent="#1a7a4a" />
          <KPICard label="Avg Completion"  value={`${summary.avg_completion}%`} />
          <KPICard label="Avg Budget Used" value={`${summary.avg_budget}%`} />
        </div>
      )}
      <div className={styles.filters}>
        <span className={styles.filterLabel}>RAG Status</span>
        {RAG_OPTIONS.map(opt => (
          <button
            key={opt}
            className={`${styles.filterChip} ${rag === opt ? styles.active : ''}`}
            onClick={() => setRag(opt)}
          >
            {opt}
          </button>
        ))}
      </div>
      <DataTable data={filtered} columns={columns} onRowClick={setDetail} />
      {detail && (
        <RecordDetail
          title={detail.project_name}
          record={detail}
          exclude={['pm_email']}
          onClose={() => setDetail(null)}
        />
      )}
      {composer && (
        <EmailComposer
          initial={buildEmailDraft(composer)}
          related={{ type: 'project', id: composer.project_id }}
          onClose={() => setComposer(null)}
        />
      )}
    </PageShell>
  )
}
