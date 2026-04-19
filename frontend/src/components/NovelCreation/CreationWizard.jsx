import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, ArrowRight, Sparkles, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../services/api'
import s from './CreationWizard.module.css'

const GENRES = [
  { key: 'romance', icon: '💕' }, { key: 'fantasy', icon: '🐉' },
  { key: 'mystery', icon: '🔍' }, { key: 'scifi', icon: '🚀' },
  { key: 'horror', icon: '👻' }, { key: 'slice_of_life', icon: '☕' },
  { key: 'action', icon: '⚔️' }, { key: 'drama', icon: '🎭' },
  { key: 'comedy', icon: '😂' }, { key: 'bl_gl', icon: '🌈' },
  { key: 'isekai', icon: '🌀' }, { key: 'other', icon: '📖' },
]

const LENGTHS = [
  { key: 'short', value: 1500 }, { key: 'medium', value: 3000 },
  { key: 'long', value: 5000 },
]

const STYLES = ['classic', 'contemporary', 'poetic', 'dark_humor', 'dark', 'sweet']
const TONES = ['balanced', 'light', 'dark', 'comedy', 'serious']
const POVS = ['first_person', 'third_person', 'omniscient']
const TOTAL_STEPS = 5

export default function CreationWizard() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [step, setStep] = useState(0)

  const [form, setForm] = useState({
    title: '',
    prompt: '',
    language: 'th',
    genre: 'fantasy',
    writing_style: 'contemporary',
    tone: 'balanced',
    pov: 'third_person',
    target_audience: 'general',
    total_chapters: 10,
    chapter_length_target: 3000,
    ai_provider: 'gemini',
  })

  const update = (field, value) => setForm(f => ({ ...f, [field]: value }))

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/api/novels/', data).then(r => r.data),
    onSuccess: (novel) => {
      queryClient.invalidateQueries(['novels', 'stats'])
      toast.success('นิยายถูกสร้างแล้ว!')
      navigate(`/novel/${novel.id}`)
    },
    onError: () => toast.error('เกิดข้อผิดพลาด'),
  })

  const handleSubmit = () => createMutation.mutate(form)
  const canNext = () => {
    if (step === 0) return form.title.length > 0 && form.prompt.length >= 10
    return true
  }

  const renderStep = () => {
    switch (step) {
      case 0: // Prompt
        return (
          <div className={s.content}>
            <h3 className={s.stepTitle}>{t('create.steps.prompt')}</h3>
            <p className={s.stepDesc}>อธิบายนิยายที่คุณต้องการให้ AI สร้าง</p>
            <div className={s.formGroup}>
              <label className={s.label}>{t('create.novel_title')}</label>
              <input className={s.input} value={form.title}
                onChange={e => update('title', e.target.value)}
                placeholder="ชื่อนิยาย..." />
            </div>
            <div className={s.formGroup}>
              <label className={s.label}>{t('create.prompt_label')}</label>
              <textarea className={s.textarea} value={form.prompt}
                onChange={e => update('prompt', e.target.value)}
                placeholder={t('create.prompt_placeholder')} />
            </div>
            <div className={s.formGroup}>
              <label className={s.label}>{t('create.language')}</label>
              <div className={s.radioGroup}>
                {[['th', '🇹🇭 ไทย'], ['en', '🇺🇸 English'], ['mixed', '🌐 ผสม']].map(([k, l]) => (
                  <button key={k} className={`${s.radioOption} ${form.language === k ? s.radioSelected : ''}`}
                    onClick={() => update('language', k)}>{l}</button>
                ))}
              </div>
            </div>
          </div>
        )

      case 1: // Genre & Style
        return (
          <div className={s.content}>
            <h3 className={s.stepTitle}>{t('create.steps.genre')}</h3>
            <p className={s.stepDesc}>เลือกแนวและสไตล์การเขียน</p>
            <div className={s.formGroup}>
              <label className={s.label}>แนวนิยาย</label>
              <div className={s.genreGrid}>
                {GENRES.map(g => (
                  <div key={g.key}
                    className={`${s.genreOption} ${form.genre === g.key ? s.genreSelected : ''}`}
                    onClick={() => update('genre', g.key)}>
                    <div className={s.genreIcon}>{g.icon}</div>
                    <div className={s.genreLabel}>{t(`genres.${g.key}`)}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className={s.twoCol}>
              <div className={s.formGroup}>
                <label className={s.label}>สไตล์การเขียน</label>
                <div className={s.radioGroup} style={{ flexDirection: 'column' }}>
                  {STYLES.map(st => (
                    <button key={st} className={`${s.radioOption} ${form.writing_style === st ? s.radioSelected : ''}`}
                      onClick={() => update('writing_style', st)}>{st}</button>
                  ))}
                </div>
              </div>
              <div>
                <div className={s.formGroup}>
                  <label className={s.label}>โทนเสียง</label>
                  <div className={s.radioGroup} style={{ flexDirection: 'column' }}>
                    {TONES.map(tn => (
                      <button key={tn} className={`${s.radioOption} ${form.tone === tn ? s.radioSelected : ''}`}
                        onClick={() => update('tone', tn)}>{tn}</button>
                    ))}
                  </div>
                </div>
                <div className={s.formGroup}>
                  <label className={s.label}>มุมมอง (POV)</label>
                  <div className={s.radioGroup} style={{ flexDirection: 'column' }}>
                    {POVS.map(p => (
                      <button key={p} className={`${s.radioOption} ${form.pov === p ? s.radioSelected : ''}`}
                        onClick={() => update('pov', p)}>{p.replace('_', ' ')}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 2: // Chapters
        return (
          <div className={s.content}>
            <h3 className={s.stepTitle}>{t('create.steps.chapters')}</h3>
            <p className={s.stepDesc}>กำหนดจำนวนตอนและความยาว</p>
            <div className={s.formGroup}>
              <label className={s.label}>{t('create.chapter_count')}</label>
              <div className={s.sliderGroup}>
                <input type="range" className={s.slider} min={1} max={100}
                  value={form.total_chapters}
                  onChange={e => update('total_chapters', parseInt(e.target.value))} />
                <div className={s.sliderValue}>{form.total_chapters}</div>
              </div>
            </div>
            <div className={s.formGroup}>
              <label className={s.label}>{t('create.chapter_length')}</label>
              <div className={s.radioGroup}>
                {LENGTHS.map(l => (
                  <button key={l.key}
                    className={`${s.radioOption} ${form.chapter_length_target === l.value ? s.radioSelected : ''}`}
                    onClick={() => update('chapter_length_target', l.value)}>
                    {t(`create.length_${l.key}`)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )

      case 3: // AI Provider
        return (
          <div className={s.content}>
            <h3 className={s.stepTitle}>{t('create.steps.ai')}</h3>
            <p className={s.stepDesc}>เลือก AI สำหรับสร้างนิยาย</p>
            <div className={s.providerGrid}>
              <div className={`${s.providerCard} ${form.ai_provider === 'gemini' ? s.providerSelected : ''}`}
                onClick={() => update('ai_provider', 'gemini')}>
                <div className={s.providerIcon}>✨</div>
                <div className={s.providerName}>Gemini 2.5 Flash</div>
                <div className={s.providerDesc}>Google AI • เร็ว • คุณภาพสูง</div>
              </div>
              <div className={`${s.providerCard} ${form.ai_provider === 'ollama' ? s.providerSelected : ''}`}
                onClick={() => update('ai_provider', 'ollama')}>
                <div className={s.providerIcon}>🦙</div>
                <div className={s.providerName}>Llama 3 8B</div>
                <div className={s.providerDesc}>Ollama • ฟรี • รันในเครื่อง</div>
              </div>
            </div>
          </div>
        )

      case 4: // Review
        return (
          <div className={s.content}>
            <h3 className={s.stepTitle}>{t('create.steps.review')}</h3>
            <p className={s.stepDesc}>ตรวจสอบการตั้งค่าก่อนเริ่มสร้าง</p>
            <div className={s.reviewGrid}>
              <div className={s.reviewItem}>
                <div className={s.reviewLabel}>ชื่อเรื่อง</div>
                <div className={s.reviewValue}>{form.title || '-'}</div>
              </div>
              <div className={s.reviewItem}>
                <div className={s.reviewLabel}>แนว</div>
                <div className={s.reviewValue}>{t(`genres.${form.genre}`)}</div>
              </div>
              <div className={s.reviewItem}>
                <div className={s.reviewLabel}>จำนวนตอน</div>
                <div className={s.reviewValue}>{form.total_chapters} ตอน</div>
              </div>
              <div className={s.reviewItem}>
                <div className={s.reviewLabel}>ความยาว/ตอน</div>
                <div className={s.reviewValue}>~{form.chapter_length_target.toLocaleString()} คำ</div>
              </div>
              <div className={s.reviewItem}>
                <div className={s.reviewLabel}>AI Provider</div>
                <div className={s.reviewValue}>{form.ai_provider === 'gemini' ? 'Gemini 2.5 Flash' : 'Llama 3 8B'}</div>
              </div>
              <div className={s.reviewItem}>
                <div className={s.reviewLabel}>ภาษา</div>
                <div className={s.reviewValue}>{form.language === 'th' ? 'ไทย' : form.language === 'en' ? 'English' : 'ผสม'}</div>
              </div>
              <div className={`${s.reviewItem} ${s.reviewPrompt}`}>
                <div className={s.reviewLabel}>เรื่องย่อ</div>
                <div className={s.reviewValue}>{form.prompt}</div>
              </div>
            </div>
          </div>
        )

      default: return null
    }
  }

  return (
    <div className={s.page}>
      <h1 className={s.title}>{t('create.title')}</h1>

      {/* Steps */}
      <div className={s.steps}>
        {Array.from({ length: TOTAL_STEPS }).map((_, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div className={`${s.step} ${i === step ? s.stepActive : ''} ${i < step ? s.stepCompleted : ''}`}>
              {i < step ? <Check size={14} /> : i + 1}
            </div>
            {i < TOTAL_STEPS - 1 && (
              <div className={`${s.connector} ${i < step ? s.connectorActive : ''}`} />
            )}
          </div>
        ))}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.25 }}
        >
          {renderStep()}
        </motion.div>
      </AnimatePresence>

      {/* Footer */}
      <div className={s.footer}>
        <button className="btn btn-secondary" onClick={() => step > 0 ? setStep(step - 1) : navigate('/')}
          disabled={createMutation.isPending}>
          <ArrowLeft size={16} />
          {t('create.back')}
        </button>

        {step < TOTAL_STEPS - 1 ? (
          <button className="btn btn-primary" onClick={() => setStep(step + 1)}
            disabled={!canNext()}>
            {t('create.next')}
            <ArrowRight size={16} />
          </button>
        ) : (
          <motion.button
            className="btn btn-primary btn-lg"
            onClick={handleSubmit}
            disabled={createMutation.isPending}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
          >
            {createMutation.isPending ? (
              <span>กำลังสร้าง...</span>
            ) : (
              <>
                <Sparkles size={18} />
                {t('create.start_generating')}
              </>
            )}
          </motion.button>
        )}
      </div>
    </div>
  )
}
