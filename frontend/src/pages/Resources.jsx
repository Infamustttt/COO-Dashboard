import { useEffect, useState, useCallback } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import api from '../api/client'
import PageShell from '../components/PageShell'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'
import EmployeeDrawer from '../components/EmployeeDrawer'
import styles from './SharedPage.module.css'

const COLUMNS = [
  { key: 'employee_id',         label: 'ID' },
  { key: 'full_name',           label: 'Name' },
  { key: 'designation',         label: 'Role' },
  { key: 'department',          label: 'Dept' },
  { key: 'utilization_status',  label: 'Status' },
  { key: 'total_allocation_pct',label: 'Allocation %', render: v => `${v}%` },
  { key: 'bench_since',         label: 'Bench Since' },
  { key: 'availability_date',   label: 'Available From' },
  { key: 'location',            label: 'Location' },
]

const BAND_COLORS = {
  'Over-allocated': '#c0392b',
  'Optimal':        '#1a7a4a',
  'Under-utilised': '#b7690a',
  'Bench':          '#3a5ba0',
}

const BAND_OPTIONS = ['All', 'Over-allocated', 'Optimal', 'Under-utilised', 'Bench']

export default function Resources() {
  const [data, setData]         = useState([])
  const [summary, setSummary]   = useState(null)
  const [deptData, setDeptData] = useState([])
  const [band, setBand]         = useState('All')
  const [selected, setSelected] = useState(null)   // employee_id for drawer

  const refetch = useCallback(() => {
    api.get('/api/employees').then(r => setData(r.data))
    api.get('/api/employees/summary').then(r => setSummary(r.data))
    api.get('/api/employees/by-department').then(r => setDeptData(r.data))
  }, [])

  useEffect(() => { refetch() }, [refetch])

  const filtered = band === 'All' ? data : data.filter(r => r.utilization_status === band)

  const bandChartData = BAND_OPTIONS.slice(1).map(b => ({
    name: b,
    count: data.filter(r => r.utilization_status === b).length,
  }))

  return (
    <PageShell title="Resource Utilisation" subtitle="Allocation bands, bench tracking and headcount">
      {summary && (
        <div className={styles.kpiRow}>
          <KPICard label="Active Employees"  value={summary.active} />
          <KPICard label="On Bench"          value={summary.bench}          accent="#3a5ba0" />
          <KPICard label="Over-allocated"    value={summary.over_allocated} accent="#c0392b" />
          <KPICard label="Optimal"           value={summary.optimal}        accent="#1a7a4a" />
          <KPICard label="Under-utilised"    value={summary.under_utilised} accent="#b7690a" />
          <KPICard label="Avg Allocation"    value={`${summary.avg_allocation}%`} />
        </div>
      )}
      <div className={styles.chartGrid}>
        <div className={styles.chartCard}>
          <p className={styles.chartTitle}>Utilisation Bands</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={bandChartData} barSize={32}>
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#6d6d70' }} />
              <YAxis tick={{ fontSize: 11, fill: '#6d6d70' }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e5e5' }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {bandChartData.map((entry, i) => (
                  <Cell key={i} fill={BAND_COLORS[entry.name] || '#a9a9ac'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className={styles.chartCard}>
          <p className={styles.chartTitle}>Headcount by Department</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={deptData} barSize={28} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 11, fill: '#6d6d70' }} />
              <YAxis type="category" dataKey="department" width={90} tick={{ fontSize: 11, fill: '#6d6d70' }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e5e5' }} />
              <Bar dataKey="count" fill="#141414" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className={styles.filters}>
        <span className={styles.filterLabel}>Band</span>
        {BAND_OPTIONS.map(opt => (
          <button
            key={opt}
            className={`${styles.filterChip} ${band === opt ? styles.active : ''}`}
            onClick={() => setBand(opt)}
          >
            {opt}
          </button>
        ))}
        <span className={styles.hint}>Click a row to view details &amp; assign</span>
      </div>
      <DataTable
        data={filtered}
        columns={COLUMNS}
        onRowClick={row => setSelected(row.employee_id)}
      />
      {selected && (
        <EmployeeDrawer
          employeeId={selected}
          onClose={() => setSelected(null)}
          onChanged={refetch}
        />
      )}
    </PageShell>
  )
}
