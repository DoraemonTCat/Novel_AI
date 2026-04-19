import { useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { BookOpen, Home, PenTool, Library, Settings, LogOut } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import api from '../../services/api'

const navItems = [
  { path: '/', icon: Home, labelKey: 'nav.dashboard' },
  { path: '/create', icon: PenTool, labelKey: 'nav.create' },
  { path: '/settings', icon: Settings, labelKey: 'nav.settings' },
]

export default function Sidebar() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)
  const user = useAuthStore((s) => s.user)

  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch (e) { /* ignore */ }
    logout()
    navigate('/login')
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
        <BookOpen size={28} style={{ color: '#8b5cf6' }} />
        <h1>Novel AI</h1>
      </div>

      <nav className="nav-section" style={{ flex: 1 }}>
        <p className="nav-section-title">{t('nav.my_novels')}</p>
        {navItems.map((item) => (
          <div
            key={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <item.icon size={18} />
            <span>{t(item.labelKey)}</span>
          </div>
        ))}
      </nav>

      <div className="nav-section" style={{ borderTop: '1px solid var(--border-color)' }}>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 12px', marginBottom: '8px' }}>
            {user.avatar_url ? (
              <img src={user.avatar_url} alt="" style={{ width: 32, height: 32, borderRadius: '50%' }} />
            ) : (
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--gradient-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 700, color: 'white' }}>
                {user.name?.[0]}
              </div>
            )}
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{user.name}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)' }}>{user.email}</div>
            </div>
          </div>
        )}
        <div className="nav-item" onClick={handleLogout} style={{ color: 'var(--error)' }}>
          <LogOut size={18} />
          <span>{t('nav.logout')}</span>
        </div>
      </div>
    </aside>
  )
}
