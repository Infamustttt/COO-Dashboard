import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const COLUMNS = [
  { key: 'client_name',     label: 'Client' },
  { key: 'survey_date',     label: 'Date' },
  { key: 'survey_type',     label: 'Type' },
  { key: 'score',           label: 'Score' },
  { key: 'nps_category',    label: 'NPS' },
  { key: 'sentiment',       label: 'Sentiment' },
  { key: 'feedback_text',   label: 'Feedback' },
  { key: 'follow_up_status',label: 'Follow-up' },
  { key: 'account_manager', label: 'Account Mgr' },
]

const NPS_COLORS    = { Promoter: '#1a7a4a', Passive: '#b7690a', Detractor: '#c0392b' }
const SENT_COLORS   = { Positive: '#1a7a4a', Neutral: '#6d6d70', Negative: '#c0392b' }
const NPS_OPTIONS   = ['All', 'Promoter', 'Passive', 'Detractor']
const SENT_OPTIONS  = ['All', 'Positive', 'Neutral', 'Negative']

export default function CSAT() {
  const [data, setData]       = useState([])
  const [summary, setSummary] = useState(null)
  const [nps, setNps]         = useState('All')
  const [sent, setSent]       = useState('All')
  const [detail, setDetail]   = useState(null)

  useEffect(() => {
    api.get('/api/csat').then(r => setData(r.data))
    api.get('/api/csat/summary').then(r => setSummary(r.data))
  }, [])

  const filtered = data
    .filter(r => nps === 'All'  || r.nps_category === nps)
    .filter(r => sent === 'All' || r.sentiment === sent)

  const npsChartData = summary ? [
    { name: 'Promoter',  value: summary.promoters  },
    { name: 'Passive',   value: summary.passives   },
    { name: 'Detractor', value: summary.detractors },
  ] : []

  const sentChartData = summary ? [
    { name: 'Positive', value: summary.positive },
    { name: 'Neutral',  value: summary.neutral  },
    { name: 'Negative', value: summary.negative },
  ] : []

  return (
    <PageShell title="Client Satisfaction" subtitle="CSAT scores, NPS categories and sentiment tracking">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Avg CSAT Score" value={summary.avg_score} sub="out of 5" />
          <KPICard label="Promoters"      value={summary.promoters}  accent="#1a7a4a" />
          <KPICard label="Passives"       value={summary.passives}   accent="#b7690a" />
          <KPICard label="Detractors"     value={summary.detractors} accent="#c0392b" />
          <KPICard label="Positive"       value={summary.positive}   accent="#1a7a4a" />
          <KPICard label="Open Follow-ups"value={summary.open_followups} accent="#b7690a" />
        </div>
      )}
      <div className={styles.chartGrid}>
        <div className={styles.chartCard}>
          <p className={styles.chartTitle}>NPS Breakdown</p>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={npsChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75} label>
                {npsChartData.map((entry, i) => (
                  <Cell key={i} fill={NPS_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e5e5' }} />
              <Legend iconSize={10} wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className={styles.chartCard}>
          <p className={styles.chartTitle}>Sentiment Distribution</p>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={sentChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75} label>
                {sentChartData.map((entry, i) => (
                  <Cell key={i} fill={SENT_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e5e5' }} />
              <Legend iconSize={10} wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className={styles.filters}>
        <span className={styles.filterLabel}>NPS</span>
        {NPS_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${nps === o ? styles.active : ''}`} onClick={() => setNps(o)}>{o}</button>
        ))}
        <span className={styles.filterLabel} style={{ marginLeft: 12 }}>Sentiment</span>
        {SENT_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${sent === o ? styles.active : ''}`} onClick={() => setSent(o)}>{o}</button>
        ))}
      </div>
      <DataTable data={filtered} columns={COLUMNS} onRowClick={setDetail} />
      {detail && (
        <RecordDetail
          title={`${detail.client_name} — ${detail.survey_type || 'CSAT'} response`}
          record={detail}
          onClose={() => setDetail(null)}
        />
      )}
    </PageShell>
  )
}
