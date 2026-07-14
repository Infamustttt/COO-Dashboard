import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './Navbar.module.css'

const PAGE_ROUTES = {
  'Executive Summary':   '/',
  'Project Delivery':    '/projects',
  'Resource Utilization': '/resources',
  'SLA Compliance':      '/sla',
  'Client Satisfaction': '/csat',
  'Escalations':         '/escalations',
  'Timesheets':          '/timesheets',
  'People Ops':          '/people',
  'SOP Library':         '/sops',
}

export default function Navbar() {
  const { user, logout } = useAuth()
  if (!user) return null

  return (
    <nav className={styles.nav}>
      <span className={styles.brand}>COO Operations Centre</span>
      <div className={styles.links}>
        {user.pages.map(page => (
          <NavLink
            key={page}
            to={PAGE_ROUTES[page]}
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.active}` : styles.link
            }
            end={PAGE_ROUTES[page] === '/'}
          >
            {page}
          </NavLink>
        ))}
      </div>
      <div className={styles.right}>
        <span className={styles.userLabel}>
          {user.name} <span className={styles.role}>{user.role}</span>
        </span>
        <button className={styles.logoutBtn} onClick={logout}>
          Log out
        </button>
      </div>
    </nav>
  )
}
