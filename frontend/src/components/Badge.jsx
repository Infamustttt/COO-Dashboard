import styles from './Badge.module.css'

const PRESETS = {
  RED:      { bg: '#fff0f0', color: '#c0392b' },
  AMBER:    { bg: '#fff8e6', color: '#b7690a' },
  GREEN:    { bg: '#f0faf3', color: '#1a7a4a' },
  P1:       { bg: '#fff0f0', color: '#c0392b' },
  P2:       { bg: '#fff8e6', color: '#b7690a' },
  P3:       { bg: '#f0f4ff', color: '#3a5ba0' },
  Met:      { bg: '#f0faf3', color: '#1a7a4a' },
  Breached: { bg: '#fff0f0', color: '#c0392b' },
  Positive: { bg: '#f0faf3', color: '#1a7a4a' },
  Neutral:  { bg: '#f5f5f5', color: '#4f4f52' },
  Negative: { bg: '#fff0f0', color: '#c0392b' },
  Open:     { bg: '#fff8e6', color: '#b7690a' },
  Resolved: { bg: '#f0faf3', color: '#1a7a4a' },
  Promoter: { bg: '#f0faf3', color: '#1a7a4a' },
  Passive:  { bg: '#fff8e6', color: '#b7690a' },
  Detractor:{ bg: '#fff0f0', color: '#c0392b' },
}

export default function Badge({ value }) {
  const preset = PRESETS[value] || { bg: '#f5f5f5', color: '#4f4f52' }
  return (
    <span
      className={styles.badge}
      style={{ background: preset.bg, color: preset.color }}
    >
      {value}
    </span>
  )
}
