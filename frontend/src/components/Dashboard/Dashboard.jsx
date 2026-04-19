import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { BookOpen, FileText, Type, Loader, Plus, Sparkles } from 'lucide-react'
import api from '../../services/api'
import styles from './Dashboard.module.css'

const GENRE_ICONS = {
  romance: '💕', fantasy: '🐉', mystery: '🔍', scifi: '🚀',
  horror: '👻', slice_of_life: '☕', action: '⚔️', drama: '🎭',
  comedy: '😂', bl_gl: '🌈', isekai: '🌀', other: '📖',
}

const statusClass = {
  draft: styles.statusDraft,
  generating: styles.statusGenerating,
  completed: styles.statusCompleted,
  error: styles.statusError,
  paused: styles.statusDraft,
}

export default function Dashboard() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => api.get('/api/novels/stats').then(r => r.data),
  })

  const { data: novels, isLoading } = useQuery({
    queryKey: ['novels'],
    queryFn: () => api.get('/api/novels/').then(r => r.data),
  })

  const statCards = [
    { icon: BookOpen, label: t('dashboard.stats.total_novels'), value: stats?.total_novels ?? 0, color: '#8b5cf6' },
    { icon: FileText, label: t('dashboard.stats.total_chapters'), value: stats?.total_chapters ?? 0, color: '#6366f1' },
    { icon: Type, label: t('dashboard.stats.total_words'), value: stats?.total_words?.toLocaleString() ?? '0', color: '#ec4899' },
    { icon: Loader, label: t('dashboard.stats.generating'), value: stats?.generating ?? 0, color: '#3b82f6' },
  ]

  return (
    <div className={styles.page}>
      {/* Stats */}
      <div className={styles.statsGrid}>
        {statCards.map((stat, i) => (
          <motion.div
            key={stat.label}
            className={styles.statCard}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className={styles.statIcon}>
              <stat.icon size={22} />
            </div>
            <div className={styles.statValue}>{stat.value}</div>
            <div className={styles.statLabel}>{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Section Header */}
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>{t('dashboard.recent')}</h2>
        <motion.button
          className={styles.createBtn}
          onClick={() => navigate('/create')}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
        >
          <Sparkles size={18} />
          {t('dashboard.create_new')}
        </motion.button>
      </div>

      {/* Novel Grid */}
      {isLoading ? (
        <div className={styles.novelGrid}>
          {[...Array(3)].map((_, i) => (
            <div key={i} className={styles.novelCard}>
              <div className={styles.novelCover} style={{ background: 'var(--bg-glass)' }}>
                <div className="skeleton" style={{ width: '100%', height: '100%' }} />
              </div>
              <div className={styles.novelBody}>
                <div className="skeleton" style={{ height: 20, width: '80%', marginBottom: 8 }} />
                <div className="skeleton" style={{ height: 14, width: '50%' }} />
              </div>
            </div>
          ))}
        </div>
      ) : novels?.length > 0 ? (
        <div className={styles.novelGrid}>
          {novels.map((novel, i) => (
            <motion.div
              key={novel.id}
              className={styles.novelCard}
              onClick={() => navigate(`/novel/${novel.id}`)}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
            >
              <div className={styles.novelCover}>
                {novel.cover_image_url ? (
                  <img src={novel.cover_image_url} alt={novel.title} />
                ) : (
                  <div className={styles.coverPlaceholder}>
                    <span style={{ fontSize: '2.5rem' }}>
                      {GENRE_ICONS[novel.genre] || '📖'}
                    </span>
                  </div>
                )}
              </div>
              <div className={styles.novelBody}>
                <div className={styles.novelTitle}>{novel.title}</div>
                <div className={styles.novelMeta}>
                  <span className={`${styles.novelStatus} ${statusClass[novel.status] || ''}`}>
                    {t(`status.${novel.status}`)}
                  </span>
                  <span>{novel.total_chapters} {t('common.chapters')}</span>
                  <span>{t(`genres.${novel.genre}`)}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <motion.div
          className={styles.emptyState}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className={styles.emptyIcon}>✨</div>
          <p className={styles.emptyText}>{t('dashboard.no_novels')}</p>
          <button className={styles.createBtn} onClick={() => navigate('/create')}>
            <Plus size={18} />
            {t('dashboard.create_new')}
          </button>
        </motion.div>
      )}
    </div>
  )
}
