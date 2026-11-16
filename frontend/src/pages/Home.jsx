import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { AnimatePresence, animate, motion, useInView, useMotionValue, useSpring, useTransform } from 'motion/react'
import { ArrowRight, Cpu, GraduationCap, Rocket } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useApi } from '../hooks/useApi'
import { getMissions, getProbes } from '../services/api'
import ProbeCard from '../components/ProbeCard'
import { Reveal } from '../components/ui'
import { asset } from '../utils/format'

const THIS_YEAR = new Date().getFullYear()
const FEATURED = ['apollo-11-eagle', 'apollo-15-lrv', 'perseverance', 'ingenuity', 'surveyor-3', 'pioneer-10', 'viking-1-orbiter', 'kepler']

function Counter({ value }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })
  const [shown, setShown] = useState(0)
  useEffect(() => {
    if (!inView) return
    const c = animate(0, value, { duration: 1.8, ease: [0.2, 0.8, 0.2, 1], onUpdate: (v) => setShown(Math.round(v)) })
    return () => c.stop()
  }, [inView, value])
  return <strong ref={ref}>{shown}</strong>
}

function HeroVisual({ dim = false }) {
  const mx = useMotionValue(0)
  const my = useMotionValue(0)
  const x = useSpring(useTransform(mx, [-1, 1], [-18, 18]), { stiffness: 60, damping: 15 })
  const y = useSpring(useTransform(my, [-1, 1], [-14, 14]), { stiffness: 60, damping: 15 })

  useEffect(() => {
    const onMove = (e) => {
      mx.set((e.clientX / window.innerWidth) * 2 - 1)
      my.set((e.clientY / window.innerHeight) * 2 - 1)
    }
    window.addEventListener('pointermove', onMove)
    return () => window.removeEventListener('pointermove', onMove)
  }, [mx, my])

  const orbits = [
    { size: '96%', duration: 60, color: 'var(--gold)' },
    { size: '78%', duration: 38, color: 'var(--mars)', reverse: true },
    { size: '112%', duration: 90, color: 'var(--cyan)' },
  ]

  return (
    <div className={`hero-visual ${dim ? 'dim' : ''}`} aria-hidden="true">
      {orbits.map((o) => (
        <motion.div key={o.size} className="orbit" style={{ width: o.size, height: o.size }} animate={{ rotate: o.reverse ? -360 : 360 }} transition={{ duration: o.duration, repeat: Infinity, ease: 'linear' }}>
          <span className="orbit-dot" style={{ background: o.color, boxShadow: `0 0 16px ${o.color}` }} />
        </motion.div>
      ))}
      <motion.div className="hero-planet" style={{ x: useTransform(x, (v) => -v * 0.5), y: useTransform(y, (v) => -v * 0.5) }} />
      <motion.img
        src={asset('/images/probes/apollo-11-lunar-module.webp')}
        alt=""
        className="hero-craft"
        style={{ x, y }}
        initial={{ opacity: 0, y: 60, scale: 0.9 }}
        animate={{ opacity: 1, y: [0, -14, 0], scale: 1 }}
        transition={{ opacity: { duration: 1 }, scale: { duration: 1.2 }, y: { duration: 6, repeat: Infinity, ease: 'easeInOut' } }}
      />
    </div>
  )
}

const STORY_CARDS = ['surveyor-3', 'apollo-15-lrv', 'perseverance']
const CARD_POSE = [
  { x: -170, y: 50, rotate: -9 },
  { x: 0, y: 10, rotate: -4 },
  { x: 170, y: -30, rotate: 2 },
]

// one screen of the story; tells the parent when it reaches the middle of the viewport
function StoryStep({ index, onActive, children }) {
  const ref = useRef(null)
  const inView = useInView(ref, { margin: '-45% 0px -45% 0px' })
  useEffect(() => {
    if (inView) onActive(index)
  }, [inView, index, onActive])
  return (
    <div ref={ref} className="story-step">
      <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ amount: 0.35 }} transition={{ duration: 0.7, ease: [0.2, 0.8, 0.2, 1] }}>
        {children}
      </motion.div>
    </div>
  )
}

const Dash = () => <span className="dash" aria-hidden="true">—</span>

function StoryCards({ cards }) {
  return (
    <motion.div className="story-cards" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      {cards.map((p, i) => (
        <motion.div
          key={p.id}
          className="story-card"
          initial={{ opacity: 0, x: 0, y: 80, rotate: 0 }}
          animate={{ opacity: 1, ...CARD_POSE[i] }}
          exit={{ opacity: 0, y: 80 }}
          transition={{ delay: i * 0.08, type: 'spring', stiffness: 120, damping: 18 }}
        >
          <ProbeCard probe={p} />
        </motion.div>
      ))}
    </motion.div>
  )
}

function Story({ list }) {
  const { t } = useTranslation()
  const [active, setActive] = useState(0)
  const cards = STORY_CARDS.map((id) => list.find((p) => p.id === id)).filter(Boolean)
  const items = (key) => t(`home.story.${key}.items`, { returnObjects: true })

  const steps = [
    <>
      <h1 className="story-title story-title-xl">
        <span>{t('home.story.s1.line1')}</span>
        <span className="hl">{t('home.story.s1.line2')}</span>
      </h1>
      <div className="mobile-only story-inline">
        <HeroVisual />
      </div>
    </>,
    <>
      <h2 className="story-title">
        <span className="hl">{t('home.story.s2.title')}</span>
      </h2>
      <ul className="story-list">
        {items('s2').map((text, i) => (
          <li key={text} className="linked">
            <Link to={['/exhibits', '/simulator', '/learn'][i]}>
              <Dash />
              <span>{text}</span>
            </Link>
          </li>
        ))}
      </ul>
    </>,
    <>
      <h2 className="story-title">
        <span>{t('home.story.s3.line1')}</span> <span className="hl">{t('home.story.s3.line2')}</span>
      </h2>
      <div className="story-planets">
        {[
          { key: 'mars', globe: 'mars', dest: 'Mars' },
          { key: 'moon', globe: 'moon', dest: 'Moon' },
          { key: 'space', globe: 'deep', dest: 'DeepSpace' },
        ].map((pl) => (
          <Link key={pl.key} to={`/exhibits?destination=${pl.dest}`} className={`story-planet ${pl.key}`}>
            <span className={`globe ${pl.globe}`} aria-hidden="true" />
            <span className="story-planet-label">
              <Dash />
              {t(`home.story.s3.${pl.key}`)}
            </span>
          </Link>
        ))}
      </div>
    </>,
    <>
      <h2 className="story-title">
        <span>{t('home.story.s4.line1')}</span>
        <span className="hl">{t('home.story.s4.line2')}</span>
      </h2>
      <p className="story-sub">{t('home.story.s4.sub')}</p>
      <ul className="story-list">
        {items('s4').map((text) => (
          <li key={text}>
            <Dash />
            <span>{text}</span>
          </li>
        ))}
      </ul>
      <div className="mobile-only rail story-rail">
        {cards.map((p) => (
          <ProbeCard key={p.id} probe={p} />
        ))}
      </div>
    </>,
    <>
      <h2 className="story-title">
        <span>{t('home.story.s5.line1')}</span>
        <span className="hl">{t('home.story.s5.line2')}</span>
      </h2>
      <p className="story-sub">{t('home.story.s5.sub')}</p>
      <ul className="story-list">
        {items('s5').map((text) => (
          <li key={text}>
            <Dash />
            <span>{text}</span>
          </li>
        ))}
      </ul>
    </>,
  ]

  return (
    <section className="story">
      <div className="container story-grid">
        <div className="story-steps">
          {steps.map((content, i) => (
            <StoryStep key={i} index={i} onActive={setActive}>
              {content}
            </StoryStep>
          ))}
        </div>
        <div className="story-visual">
          <div className="story-sticky">
            <HeroVisual dim={active === 3} />
            <AnimatePresence>{active === 3 && <StoryCards key="cards" cards={cards} />}</AnimatePresence>
          </div>
        </div>
      </div>
      <div className="hero-scroll" aria-hidden="true">
        {t('home.scroll')}
        <motion.span className="line" animate={{ scaleY: [0.3, 1, 0.3], originY: 0 }} transition={{ duration: 2, repeat: Infinity }} />
      </div>
    </section>
  )
}

export default function Home() {
  const { t } = useTranslation()
  const probes = useApi(() => getProbes())
  const missions = useApi(() => getMissions())
  const list = probes.data ?? []

  const count = (dests) => list.filter((p) => dests.includes(p.destination)).length
  const years = list.length ? THIS_YEAR - Math.min(...list.map((p) => Number(p.launch.slice(0, 4)))) : 0
  const featured = FEATURED.map((id) => list.find((p) => p.id === id)).filter(Boolean)

  return (
    <>
      <Story list={list} />

      <section className="container">
        <div className="stats">
          <div className="stat"><Counter value={list.length} /><span>{t('home.stats.artifacts')}</span></div>
          <div className="stat"><Counter value={new Set(list.map((p) => p.destination)).size} /><span>{t('home.stats.destinations')}</span></div>
          <div className="stat"><Counter value={missions.data?.length ?? 0} /><span>{t('home.stats.missions')}</span></div>
          <div className="stat"><Counter value={years} /><span>{t('home.stats.years')}</span></div>
        </div>
      </section>

      <section className="section container">
        <Reveal>
          <span className="eyebrow">{t('nav.exhibits')}</span>
          <h2 className="section-title">{t('home.destTitle')}</h2>
          <p className="section-lead">{t('home.destLead')}</p>
        </Reveal>
        <div className="destinations">
          {[
            { key: 'Moon', globe: 'moon', desc: 'destMoon', dests: ['Moon'] },
            { key: 'Mars', globe: 'mars', desc: 'destMars', dests: ['Mars'] },
            { key: 'DeepSpace', globe: 'deep', desc: 'destDeep', dests: ['Asteroid', 'DeepSpace'] },
          ].map((d, i) => (
            <Reveal key={d.key} delay={i * 0.1}>
              <Link to={`/exhibits?destination=${d.key}`} className="destination">
                <span className={`globe ${d.globe}`} aria-hidden="true" />
                <h3>{t(`destination.${d.key}`)}</h3>
                <p>{t(`home.${d.desc}`)}</p>
                <span className="count">
                  {t('home.artifacts', { count: count(d.dests) })} <ArrowRight size={14} />
                </span>
              </Link>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="section-sm container">
        <Reveal className="row-head">
          <div>
            <span className="eyebrow">{t('exhibits.eyebrow')}</span>
            <h2 className="section-title">{t('home.featuredTitle')}</h2>
            <p className="section-lead">{t('home.featuredLead')}</p>
          </div>
          <Link to="/exhibits" className="btn">
            {t('common.viewAll')} <ArrowRight size={16} />
          </Link>
        </Reveal>
        <div className="rail">
          {featured.map((p) => (
            <ProbeCard key={p.id} probe={p} />
          ))}
        </div>
      </section>

      <section className="section container">
        <Reveal className="cta-band">
          <div>
            <span className="eyebrow">
              <Cpu size={14} /> {t('sim.eyebrow')}
            </span>
            <h2 className="section-title">{t('home.simTitle')}</h2>
            <p className="section-lead">{t('home.simLead')}</p>
            <Link to="/simulator" className="btn btn-primary" style={{ marginTop: 28 }}>
              <Rocket size={18} /> {t('home.simCta')}
            </Link>
          </div>
          <motion.img src={asset('/images/probes/apollo-15-lrv.webp')} alt="" animate={{ y: [0, -10, 0] }} transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }} />
        </Reveal>
      </section>

      <section className="section-sm container" style={{ paddingBottom: 110 }}>
        <Reveal className="cta-band" >
          <motion.img src={asset('/images/probes/apollo-11-plaque.webp')} alt="" animate={{ y: [0, -8, 0] }} transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }} />
          <div>
            <span className="eyebrow">
              <GraduationCap size={14} /> {t('learn.eyebrow')}
            </span>
            <h2 className="section-title">{t('home.learnTitle')}</h2>
            <p className="section-lead">{t('home.learnLead')}</p>
            <Link to="/learn" className="btn" style={{ marginTop: 28 }}>
              {t('home.learnCta')} <ArrowRight size={16} />
            </Link>
          </div>
        </Reveal>
      </section>
    </>
  )
}
