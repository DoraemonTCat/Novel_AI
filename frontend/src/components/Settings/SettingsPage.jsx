import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { Settings, Palette, Globe, Key, Monitor } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'
import { useAuthStore } from '../../stores/authStore'
import s from './SettingsPage.module.css'

export default function SettingsPage() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme, language, setLanguage } = useUIStore()
  const user = useAuthStore(st => st.user)

  return (
    <motion.div className={s.page} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <h1 className={s.title}>{t('nav.settings')}</h1>

      {/* Account */}
      <div className={s.section}>
        <h3 className={s.sectionTitle}><Key size={18} /> Account</h3>
        <div className={s.row}>
          <span className={s.rowLabel}>Email</span>
          <span className={s.rowValue}>{user?.email || '-'}</span>
        </div>
        <div className={s.row}>
          <span className={s.rowLabel}>Name</span>
          <span className={s.rowValue}>{user?.name || '-'}</span>
        </div>
      </div>

      {/* UI Preferences */}
      <div className={s.section}>
        <h3 className={s.sectionTitle}><Palette size={18} /> UI Preferences</h3>
        <div className={s.row}>
          <span className={s.rowLabel}>Theme</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className={`btn btn-sm ${theme === 'dark' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTheme('dark')}
            >🌙 Dark</button>
            <button
              className={`btn btn-sm ${theme === 'light' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTheme('light')}
            >☀️ Light</button>
          </div>
        </div>
        <div className={s.row}>
          <span className={s.rowLabel}>Language / ภาษา</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className={`btn btn-sm ${language === 'th' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => { setLanguage('th'); i18n.changeLanguage('th') }}
            >🇹🇭 ไทย</button>
            <button
              className={`btn btn-sm ${language === 'en' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => { setLanguage('en'); i18n.changeLanguage('en') }}
            >🇺🇸 EN</button>
          </div>
        </div>
      </div>

      {/* AI Configuration */}
      <div className={s.section}>
        <h3 className={s.sectionTitle}><Monitor size={18} /> AI Configuration</h3>
        <div className={s.row}>
          <span className={s.rowLabel}>Gemini Model</span>
          <span className={s.rowValue}>models/gemini-2.5-flash</span>
        </div>
        <div className={s.row}>
          <span className={s.rowLabel}>Ollama Model</span>
          <span className={s.rowValue}>llama3:8b</span>
        </div>
        <div className={s.row}>
          <span className={s.rowLabel}>Ollama Status</span>
          <span className={s.rowValue} style={{ color: 'var(--text-tertiary)' }}>ต้องเปิดด้วย --profile with-ollama</span>
        </div>
      </div>
    </motion.div>
  )
}
