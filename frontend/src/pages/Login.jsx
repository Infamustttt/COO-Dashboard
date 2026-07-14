import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './Login.module.css'

export default function Login() {
  const { login }           = useAuth()
  const navigate             = useNavigate()
  const [username, setUser]  = useState('')
  const [password, setPass]  = useState('')
  const [error, setError]    = useState('')
  const [loading, setLoading]= useState(false)

  const submit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/')
    } catch {
      setError('Invalid username or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.eyebrow}>Operations Command Centre</div>
        <h1 className={styles.heading}>Sign in</h1>
        <form className={styles.form} onSubmit={submit}>
          <label className={styles.label}>
            Username
            <input
              className={styles.input}
              value={username}
              onChange={e => setUser(e.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label className={styles.label}>
            Password
            <input
              className={styles.input}
              type="password"
              value={password}
              onChange={e => setPass(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          {error && <p className={styles.error}>{error}</p>}
          <button className={styles.btn} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <div className={styles.hint}>
          <span>COO: aarush / coo123</span>
          <span>DM: delivery_mgr / del123</span>
          <span>HR: muskaan / hr123</span>
        </div>
      </div>
    </div>
  )
}
