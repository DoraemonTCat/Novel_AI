import { useTranslation } from 'react-i18next'
import { Globe, Sun, Moon, Menu } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'

export default function Header() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme, toggleSidebar, language, setLanguage } = useUIStore()

  const toggleLanguage = () => {
    const newLang = language === 'th' ? 'en' : 'th'
    i18n.changeLanguage(newLang)
    setLanguage(newLang)
  }

  return (
    <header className="header">
      <button className="btn btn-ghost btn-icon" onClick={toggleSidebar}>
        <Menu size={20} />
      </button>

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          className="btn btn-ghost btn-sm"
          onClick={toggleLanguage}
          title="Toggle Language"
        >
          <Globe size={16} />
          <span>{language === 'th' ? 'TH' : 'EN'}</span>
        </button>

        <button
          className="btn btn-ghost btn-icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  )
}
