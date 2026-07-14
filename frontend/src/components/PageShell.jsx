import styles from './PageShell.module.css'

export default function PageShell({ title, subtitle, children }) {
  return (
    <div className={styles.shell}>
      <div className={styles.header}>
        <h1 className={styles.title}>{title}</h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}
