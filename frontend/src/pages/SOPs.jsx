import { useEffect, useState } from 'react'
import api from '../api/client'
import PageShell from '../components/PageShell'
import DataTable from '../components/DataTable'
import RecordDetail from '../components/RecordDetail'
import styles from './SharedPage.module.css'

const COLUMNS = [
  { key: 'sop_id',   label: 'SOP ID' },
  { key: 'title',    label: 'Title' },
  { key: 'category', label: 'Category' },
  { key: 'version',  label: 'Version' },
  { key: 'owner',    label: 'Owner' },
  { key: 'last_updated', label: 'Last Updated' },
  { key: 'status',   label: 'Status' },
  { key: 'document_url', label: 'Link', render: v => (
    <a
      href={v}
      target="_blank"
      rel="noreferrer"
      onClick={e => e.stopPropagation()}
      style={{ color: '#141414', textDecoration: 'underline', fontSize: 12 }}
    >
      Open
    </a>
  )},
]

const CAT_OPTIONS = ['All', 'HR', 'Delivery', 'Client Management']

export default function SOPs() {
  const [data, setData]     = useState([])
  const [cat, setCat]       = useState('All')
  const [detail, setDetail] = useState(null)

  useEffect(() => {
    api.get('/api/sops').then(r => setData(r.data))
  }, [])

  const filtered = cat === 'All' ? data : data.filter(r => r.category === cat)

  return (
    <PageShell title="SOP Library" subtitle="Standard operating procedures by category">
      <div className={styles.filters}>
        <span className={styles.filterLabel}>Category</span>
        {CAT_OPTIONS.map(o => (
          <button key={o} className={`${styles.filterChip} ${cat === o ? styles.active : ''}`} onClick={() => setCat(o)}>{o}</button>
        ))}
      </div>
      <DataTable data={filtered} columns={COLUMNS} pageSize={10} onRowClick={setDetail} />
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
