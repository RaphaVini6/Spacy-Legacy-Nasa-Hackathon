import { ExternalLink } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Reveal } from '../components/ui'
import { CONTENT, SOFTWARE } from '../data/licenses'

// open-source licenses of everything the project uses (requested by the hackathon reviewers)
export default function Licenses() {
  const { t } = useTranslation()
  return (
    <div className="container" style={{ paddingBottom: 100 }}>
      <Reveal className="page-head">
        <span className="eyebrow">{t('licenses.eyebrow')}</span>
        <h1>{t('licenses.title')}</h1>
        <p className="section-lead">{t('licenses.lead')}</p>
      </Reveal>

      {SOFTWARE.map((g) => (
        <section key={g.group} className="section-sm">
          <h2 className="subsection-title" style={{ marginTop: 0 }}>{t(`licenses.group.${g.group}`)}</h2>
          <div className="table-wrap">
            <table className="licenses">
              <thead>
                <tr>
                  <th scope="col">{t('licenses.name')}</th>
                  <th scope="col">{t('licenses.version')}</th>
                  <th scope="col">{t('licenses.license')}</th>
                </tr>
              </thead>
              <tbody>
                {g.items.map((i) => (
                  <tr key={i.name}>
                    <td>
                      <a href={i.url} target="_blank" rel="noreferrer">
                        {i.name} <ExternalLink size={12} aria-hidden="true" />
                      </a>
                    </td>
                    <td>{i.version}</td>
                    <td>
                      <a href={`https://spdx.org/licenses/${i.license}.html`} target="_blank" rel="noreferrer" className="license-tag">
                        {i.license}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}

      <section className="section-sm">
        <h2 className="subsection-title" style={{ marginTop: 0 }}>{t('licenses.group.content')}</h2>
        <div className="two-col" style={{ marginTop: 20 }}>
          {CONTENT.map((c) => (
            <div key={c.key} className="card">
              <h3>{t(`licenses.content.${c.key}.title`)}</h3>
              <p>{t(`licenses.content.${c.key}.text`)}</p>
              {c.url && (
                <a className="license-link" href={c.url} target="_blank" rel="noreferrer">
                  {c.url.replace(/^https:\/\//, '')} <ExternalLink size={12} aria-hidden="true" />
                </a>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
