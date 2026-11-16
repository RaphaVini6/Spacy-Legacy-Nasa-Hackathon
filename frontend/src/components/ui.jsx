import { useEffect, useId, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { ChevronDown } from 'lucide-react'
import { useTranslation } from 'react-i18next'

// small shared pieces

// "Learn more": the main text is written for teenagers, the details keep the technical wording for research
export function LearnMore({ details }) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const id = useId()
  if (!details) return null
  return (
    <div className="learn-more">
      <button type="button" className="learn-more-btn" aria-expanded={open} aria-controls={id} onClick={() => setOpen((o) => !o)}>
        {open ? t('common.showLess') : t('common.learnMore')}
        <ChevronDown size={16} style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} aria-hidden="true" />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div id={id} className="learn-more-body" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}>
            <p>{details}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function Reveal({ children, delay = 0, y = 24, className, as = 'div' }) {
  const Tag = motion[as]
  return (
    <Tag className={className} initial={{ opacity: 0, y }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-60px' }} transition={{ duration: 0.6, delay, ease: [0.2, 0.8, 0.2, 1] }}>
      {children}
    </Tag>
  )
}

export function StatusBadge({ status }) {
  const { t } = useTranslation()
  return (
    <span className={`badge badge-${status}`}>
      <span className="dot" />
      {t(`status.${status}`)}
    </span>
  )
}

export function DestinationBadge({ destination }) {
  const { t } = useTranslation()
  return <span className={`badge badge-${destination}`}>{t(`destination.${destination}`)}</span>
}

export function Loader() {
  const { t } = useTranslation()
  // the hosted backend sleeps when idle; tell the visitor why the first load is slow
  const [slow, setSlow] = useState(false)
  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), 6000)
    return () => clearTimeout(timer)
  }, [])
  return (
    <div className="loader" role="status">
      <div className="loader-orbit" />
      {slow ? <p className="loader-hint">{t('common.wakingUp')}</p> : <span className="sr-only">{t('common.loading')}</span>}
    </div>
  )
}

export function ErrorBox({ onRetry }) {
  const { t } = useTranslation()
  return (
    <div className="error-box" role="alert">
      <p>{t('common.error')}</p>
      {onRetry && (
        <button type="button" className="btn btn-sm" style={{ marginTop: 12 }} onClick={onRetry}>
          {t('common.retry')}
        </button>
      )}
    </div>
  )
}
