import { Component } from 'react'
import { useTranslation } from 'react-i18next'
import { RotateCw } from 'lucide-react'

function ErrorScreen() {
  const { t } = useTranslation()
  return (
    <div className="container section" role="alert" style={{ textAlign: 'center' }}>
      <h1 className="section-title">{t('common.pageError')}</h1>
      <p className="section-lead" style={{ margin: '14px auto 28px' }}>{t('common.pageErrorLead')}</p>
      <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>
        <RotateCw size={18} /> {t('common.reload')}
      </button>
    </div>
  )
}

// keeps the header and footer on screen when a page crashes, instead of a blank (black) site.
// Layout remounts it on every route change, which clears the error.
export default class PageErrorBoundary extends Component {
  state = { error: null }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    return this.state.error ? <ErrorScreen /> : this.props.children
  }
}
