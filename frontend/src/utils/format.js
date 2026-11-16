// NASA images fill the frame; the team's 3D renders are cut out and float
// (surveyor-3 is a team render that has its own background)
export const isPhoto = (probe) =>
  (probe?.image?.kind != null && probe.image.kind !== 'TeamIllustration') || Boolean(probe?.imageUrl?.includes('surveyor-3'))

export function formatDate(value, lang) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value ?? '')) return value
  return new Date(`${value}T12:00:00Z`).toLocaleDateString(lang, { day: 'numeric', month: 'long', year: 'numeric' })
}
