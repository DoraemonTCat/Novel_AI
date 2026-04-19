import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Pause, Download, BookOpen, FileText, Users, ChevronLeft, ChevronRight, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../services/api'
import s from './NovelDetail.module.css'

const GENRE_ICONS = {
  romance: '💕', fantasy: '🐉', mystery: '🔍', scifi: '🚀',
  horror: '👻', slice_of_life: '☕', action: '⚔️', drama: '🎭',
  comedy: '😂', bl_gl: '🌈', isekai: '🌀', other: '📖',
}

export default function NovelDetail() {
  const { novelId } = useParams()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('chapters')
  const [selectedChapterId, setSelectedChapterId] = useState(null)
  const [readerChapterNum, setReaderChapterNum] = useState(1)

  const { data: novel, isLoading: novelLoading } = useQuery({
    queryKey: ['novel', novelId],
    queryFn: () => api.get(`/api/novels/${novelId}`).then(r => r.data),
  })

  const { data: chapters } = useQuery({
    queryKey: ['chapters', novelId],
    queryFn: () => api.get(`/api/novels/${novelId}/chapters/`).then(r => r.data),
    enabled: !!novelId,
  })

  // Fetch full chapter content when a chapter is selected
  const { data: fullChapter, isLoading: chapterLoading } = useQuery({
    queryKey: ['chapter', novelId, selectedChapterId],
    queryFn: () => api.get(`/api/novels/${novelId}/chapters/${selectedChapterId}`).then(r => r.data),
    enabled: !!selectedChapterId && !!novelId,
  })

  const startGenMutation = useMutation({
    mutationFn: () => api.post('/api/generation/start', { novel_id: novelId }),
    onSuccess: () => {
      toast.success('เริ่มสร้างนิยายแล้ว!')
      queryClient.invalidateQueries(['novel', novelId])
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Error'),
  })

  // WebSocket for real-time progress
  const [progress, setProgress] = useState(null)
  useEffect(() => {
    if (novel?.status !== 'generating' || !novel?.celery_task_id) return

    const wsUrl = `ws://localhost:8000/ws/generation/${novel.celery_task_id}`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        setProgress(data)
        if (data.status === 'completed') {
          queryClient.invalidateQueries(['novel', novelId])
          queryClient.invalidateQueries(['chapters', novelId])
          toast.success('สร้างนิยายเสร็จแล้ว! 🎉')
        }
      }
    }

    return () => ws.close()
  }, [novel?.status, novel?.celery_task_id])

  // Open chapter in reader
  const openChapter = (ch) => {
    setSelectedChapterId(ch.id)
    setReaderChapterNum(ch.chapter_number)
    setActiveTab('read')
  }

  // Navigate to prev/next chapter
  const goPrev = () => {
    if (!chapters || readerChapterNum <= 1) return
    const prev = chapters.find(c => c.chapter_number === readerChapterNum - 1)
    if (prev) openChapter(prev)
  }

  const goNext = () => {
    if (!chapters || readerChapterNum >= chapters.length) return
    const next = chapters.find(c => c.chapter_number === readerChapterNum + 1)
    if (next) openChapter(next)
  }

  if (novelLoading) {
    return (
      <div className={s.page}>
        <div className={s.header}>
          <div className={s.cover}><div className="skeleton" style={{ width: '100%', height: '100%' }} /></div>
          <div className={s.info}>
            <div className="skeleton" style={{ height: 30, width: '60%', marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 18, width: '40%' }} />
          </div>
        </div>
      </div>
    )
  }

  if (!novel) return <div className={s.page}>Novel not found</div>

  const completedChapters = chapters?.filter(c => c.status === 'completed').length || 0
  const progressPercent = progress?.progress_percent ?? (completedChapters / novel.total_chapters * 100)

  return (
    <div className={s.page}>
      {/* Header */}
      <motion.div className={s.header} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className={s.cover}>
          {novel.cover_image_url ? (
            <img src={novel.cover_image_url} alt={novel.title} />
          ) : (
            GENRE_ICONS[novel.genre] || '📖'
          )}
        </div>
        <div className={s.info}>
          <h1 className={s.novelTitle}>{novel.title}</h1>
          <div className={s.novelMeta}>
            <span className={s.metaTag}>{t(`genres.${novel.genre}`)}</span>
            <span className={s.metaTag}>{novel.ai_provider === 'gemini' ? 'Gemini 2.5' : 'Llama 3'}</span>
            <span className={s.metaTag}>{novel.language === 'th' ? '🇹🇭 ไทย' : '🇺🇸 EN'}</span>
            <span className={s.metaTag}>{novel.total_chapters} ตอน</span>
          </div>

          {/* Progress */}
          {(novel.status === 'generating' || novel.status === 'completed') && (
            <div className={s.progressSection}>
              <div className={s.progressText}>
                {progress?.message || `${completedChapters}/${novel.total_chapters} ตอน`}
              </div>
              <div className={s.progressBar}>
                <motion.div 
                  className={s.progressFill}
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          )}

          <div className={s.actions}>
            {novel.status === 'draft' && (
              <button className="btn btn-primary" onClick={() => startGenMutation.mutate()}
                disabled={startGenMutation.isPending}>
                <Play size={16} /> เริ่มสร้าง
              </button>
            )}
            {novel.status === 'completed' && (
              <button className="btn btn-primary">
                <Download size={16} /> Export
              </button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className={s.tabs}>
        {[
          { key: 'chapters', label: 'ตอน', icon: FileText },
          { key: 'read', label: 'อ่าน', icon: BookOpen },
          { key: 'characters', label: 'ตัวละคร', icon: Users },
        ].map(tab => (
          <button key={tab.key}
            className={`${s.tab} ${activeTab === tab.key ? s.tabActive : ''}`}
            onClick={() => setActiveTab(tab.key)}>
            <tab.icon size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'chapters' && (
        <div className={s.chaptersList}>
          {chapters?.length > 0 ? (
            chapters.map(ch => (
              <motion.div key={ch.id} className={s.chapterItem}
                onClick={() => openChapter(ch)}
                style={{ cursor: 'pointer' }}
                whileHover={{ scale: 1.01, backgroundColor: 'rgba(139,92,246,0.08)' }}
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: ch.chapter_number * 0.03 }}>
                <div className={s.chapterNum}>{ch.chapter_number}</div>
                <div className={s.chapterInfo}>
                  <div className={s.chapterTitle}>{ch.title || `ตอนที่ ${ch.chapter_number}`}</div>
                  <div className={s.chapterMeta}>
                    {ch.word_count.toLocaleString()} {t('common.words')}
                  </div>
                </div>
                <span className={s.chapterStatus} style={{
                  background: ch.status === 'completed' ? 'rgba(34,197,94,0.15)' : 'rgba(59,130,246,0.15)',
                  color: ch.status === 'completed' ? 'var(--success)' : 'var(--info)',
                }}>
                  {t(`status.${ch.status}`)}
                </span>
              </motion.div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)' }}>
              {novel.status === 'draft' ? 'กดเริ่มสร้างเพื่อสร้างตอน' : 'กำลังสร้าง...'}
            </div>
          )}
        </div>
      )}

      {activeTab === 'read' && (
        <div className={s.readerPanel}>
          {selectedChapterId ? (
            chapterLoading ? (
              <div className={s.readerLoading}>
                <div className={s.loadingSpinner} />
                <p>กำลังโหลดเนื้อหา...</p>
              </div>
            ) : fullChapter ? (
              <>
                {/* Chapter navigation header */}
                <div className={s.readerNav}>
                  <button 
                    className={s.navBtn} 
                    onClick={goPrev}
                    disabled={readerChapterNum <= 1}>
                    <ChevronLeft size={18} /> ตอนก่อนหน้า
                  </button>
                  <span className={s.navTitle}>
                    ตอนที่ {fullChapter.chapter_number}: {fullChapter.title}
                  </span>
                  <button 
                    className={s.navBtn} 
                    onClick={goNext}
                    disabled={!chapters || readerChapterNum >= chapters.length}>
                    ตอนถัดไป <ChevronRight size={18} />
                  </button>
                </div>

                {/* Chapter content */}
                <motion.div 
                  className={s.readerContent}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  key={fullChapter.id}>
                  <h2 className={s.readerTitle}>
                    {fullChapter.title || `ตอนที่ ${fullChapter.chapter_number}`}
                  </h2>
                  <div className={s.readerMeta}>
                    {fullChapter.word_count.toLocaleString()} คำ • 
                    เวอร์ชัน {fullChapter.current_version}
                  </div>
                  <div className={s.readerText}>
                    {fullChapter.content}
                  </div>
                </motion.div>

                {/* Bottom navigation */}
                <div className={s.readerNav} style={{ marginTop: 40 }}>
                  <button className={s.navBtn} onClick={goPrev} disabled={readerChapterNum <= 1}>
                    <ChevronLeft size={18} /> ตอนก่อนหน้า
                  </button>
                  <button className={s.navBtn} onClick={() => { setActiveTab('chapters'); setSelectedChapterId(null) }}>
                    <ArrowLeft size={18} /> กลับรายการ
                  </button>
                  <button className={s.navBtn} onClick={goNext} disabled={!chapters || readerChapterNum >= chapters.length}>
                    ตอนถัดไป <ChevronRight size={18} />
                  </button>
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)' }}>
                ไม่พบเนื้อหาตอนนี้
              </div>
            )
          ) : (
            <div className={s.readerEmpty}>
              <BookOpen size={48} strokeWidth={1} />
              <h3>เลือกตอนที่ต้องการอ่าน</h3>
              <p>ไปที่แท็บ "ตอน" แล้วกดเลือกตอนที่ต้องการ</p>
              <button className="btn btn-primary" onClick={() => setActiveTab('chapters')}>
                <FileText size={16} /> ไปที่รายการตอน
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'characters' && (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)' }}>
          🚧 Character Manager — Coming Soon
        </div>
      )}
    </div>
  )
}
