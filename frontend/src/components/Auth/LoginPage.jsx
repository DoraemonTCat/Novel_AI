import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { BookOpen } from 'lucide-react'
import api from '../../services/api'

export default function LoginPage() {
  const { t } = useTranslation()

  const handleGoogleLogin = async () => {
    try {
      const res = await api.get('/api/auth/google/login')
      window.location.href = res.data.auth_url
    } catch (err) {
      console.error('Login error:', err)
    }
  }

  return (
    <div className="login-page">
      <motion.div
        className="login-card glass-card"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          style={{ marginBottom: '20px' }}
        >
          <BookOpen size={48} style={{ color: '#8b5cf6' }} />
        </motion.div>

        <h1>{t('login.title')}</h1>
        <p>{t('login.subtitle')}</p>

        <motion.button
          className="google-btn"
          onClick={handleGoogleLogin}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          {t('login.google_btn')}
        </motion.button>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          style={{ marginTop: '24px', fontSize: '0.75rem', color: 'var(--text-tertiary)' }}
        >
          {t('login.description')}
        </motion.p>
      </motion.div>
    </div>
  )
}
