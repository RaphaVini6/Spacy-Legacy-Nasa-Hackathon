// NASA photos fill the frame; the team's 3D renders are cut out and float
export const isPhoto = (probe) => Boolean(probe?.imageCredit) || Boolean(probe?.imageUrl?.includes('surveyor-3'))

// public files (images) live under the site base path, e.g. /Spacy-Legacy-Nasa-Hackathon/ on GitHub Pages
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '')
export const asset = (path) => (path?.startsWith('/') ? `${BASE}${path}` : path)

export function formatDate(value, lang) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value ?? '')) return value
  return new Date(`${value}T12:00:00Z`).toLocaleDateString(lang, { day: 'numeric', month: 'long', year: 'numeric' })
}
