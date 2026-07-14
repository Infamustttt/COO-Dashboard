import styles from './KPICard.module.css'

export default function KPICard({ label, value, sub, accent }) {
  return (
    <div className={styles.card}>
      <span className={styles.label}>{label}</span>
      <span className={styles.value} style={accent ? { color: accent } : {}}>
        {value ?? '—'}
      </span>
      {sub && <span className={styles.sub}>{sub}</span>}
    </div>
  )
}
