import { useTranslation } from 'react-i18next'
import { LANGUAGES } from '../i18n'

// changes UI language and reloads backend content in that language
// `id` lets the header and the mobile menu each have their own copy
export default function LanguageSwitcher({ id = 'language' }) {
  const { t, i18n } = useTranslation()
  return (
    <>
      <label htmlFor={id} className="sr-only">
        {t('language.label')}
      </label>
      <select id={id} className="select" value={i18n.resolvedLanguage} onChange={(e) => i18n.changeLanguage(e.target.value)}>
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code} lang={l.code}>
            {l.label}
          </option>
        ))}
      </select>
    </>
  )
}
