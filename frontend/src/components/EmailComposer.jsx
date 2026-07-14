import { useState } from 'react'
import api from '../api/client'
import Modal from './Modal'
import styles from './EmailComposer.module.css'

/**
 * Reusable email composer. Drop into any page:
 *   <EmailComposer
 *     initial={{ to, subject, body }}
 *     related={{ type: 'project', id: 'PROJ-004' }}
 *     onClose={() => setComposer(null)}
 *   />
 */
export default function EmailComposer({ initial = {}, related, onClose }) {
  const [to, setTo]           = useState(initial.to || '')
  const [subject, setSubject] = useState(initial.subject || '')
  const [body, setBody]       = useState(initial.body || '')
  const [sending, setSending] = useState(false)
  const [sent, setSent]       = useState(false)
  const [error, setError]     = useState(null)

  const send = async () => {
    setSending(true)
    setError(null)
    try {
      await api.post('/api/emails', {
        to, subject, body,
        related_type: related?.type ?? null,
        related_id: related?.id ?? null,
      })
      setSent(true)
      setTimeout(onClose, 1200)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <Modal title="New Email" onClose={onClose}>
      {sent ? (
        <div className={styles.sentState}>
          <span className={styles.sentIcon}>✓</span>
          <p>Email sent to {to}</p>
        </div>
      ) : (
        <div className={styles.form}>
          <label className={styles.label}>
            To
            <input className={styles.input} value={to} onChange={e => setTo(e.target.value)} />
          </label>
          <label className={styles.label}>
            Subject
            <input className={styles.input} value={subject} onChange={e => setSubject(e.target.value)} />
          </label>
          <label className={styles.label}>
            Message
            <textarea
              className={styles.textarea}
              rows={10}
              value={body}
              onChange={e => setBody(e.target.value)}
            />
          </label>
          {error && <p className={styles.error}>{error}</p>}
          <div className={styles.actions}>
            <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
            <button
              className={styles.sendBtn}
              onClick={send}
              disabled={sending || !to || !subject}
            >
              {sending ? 'Sending…' : 'Send Email'}
            </button>
          </div>
        </div>
      )}
    </Modal>
  )
}
