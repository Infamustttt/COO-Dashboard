import Modal from './Modal'
import Badge from './Badge'
import styles from './RecordDetail.module.css'

const BADGE_KEYS = new Set([
  'rag_status', 'severity', 'compliance_status', 'sentiment',
  'nps_category', 'status', 'utilization_status', 'approval_status',
  'submission_status',
])

const prettify = key =>
  key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
     .replace(/\bPct\b/, '%').replace(/\bId\b/, 'ID').replace(/\bUrl\b/, 'URL')

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (Array.isArray(value)) return value.join(', ')
  const s = String(value)
  // trim "2026-06-10 00:00:00" style timestamps to the date
  if (/^\d{4}-\d{2}-\d{2}[T ]00:00(:00)?/.test(s)) return s.slice(0, 10)
  return s
}

/**
 * Generic read-only detail modal for any table row.
 * <RecordDetail title={row.project_name} record={row} onClose={fn} exclude={['pm_email']} />
 */
export default function RecordDetail({ title, record, onClose, exclude = [] }) {
  const skip = new Set(exclude)
  const entries = Object.entries(record).filter(([k]) => !skip.has(k))

  return (
    <Modal title={title || 'Details'} onClose={onClose} wide>
      <div className={styles.grid}>
        {entries.map(([key, value]) => {
          const long = typeof value === 'string' && value.length > 80
          return (
            <div key={key} className={`${styles.field} ${long ? styles.full : ''}`}>
              <span className={styles.label}>{prettify(key)}</span>
              {BADGE_KEYS.has(key) && value
                ? <span><Badge value={value} /></span>
                : <span className={styles.value}>{formatValue(value)}</span>}
            </div>
          )
        })}
      </div>
    </Modal>
  )
}
