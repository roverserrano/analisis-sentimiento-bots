import { useMemo, useState } from 'react'
import { Download, Loader2 } from 'lucide-react'
import BotChart from '../charts/BotChart'
import SentimentChart from '../charts/SentimentChart'
import FileUpload from '../components/FileUpload'
import { analyzeCsv, getApiErrorMessage } from '../services/api'

const PAGE_SIZE = 10

function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`
}

function csvEscape(value) {
  return `"${String(value ?? '').replaceAll('"', '""')}"`
}

function BulkAnalysis() {
  const [file, setFile] = useState(null)
  const [response, setResponse] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const results = useMemo(() => response?.resultados || [], [response])
  const totalPages = Math.max(1, Math.ceil(results.length / PAGE_SIZE))
  const visibleRows = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE
    return results.slice(start, start + PAGE_SIZE)
  }, [page, results])

  async function handleAnalyze() {
    if (!file) {
      setError('Selecciona un archivo CSV antes de analizar.')
      return
    }

    setLoading(true)
    setError('')
    setPage(1)

    try {
      const result = await analyzeCsv(file)
      setResponse(result)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  function exportResults() {
    const header = ['#', 'Comentario', 'Sentimiento', 'Confianza S.', 'Bot', 'Confianza B.']
    const rows = results.map((item, index) => [
      index + 1,
      item.comentario,
      item.sentimiento.clase,
      item.sentimiento.confianza,
      item.bot.clase,
      item.bot.confianza,
    ])
    const csv = [header, ...rows].map((row) => row.map(csvEscape).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'sentinelai_resultados.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="bulk-page">
      <section className="hero-panel">
        <span className="section-kicker">Analisis masivo</span>
        <h1>Procesa lotes de comentarios desde CSV.</h1>
        <p>
          Sube un archivo con columna comentario y SentinelAI generara tabla, resumen y graficos
          para tu defensa academica.
        </p>
      </section>

      <section className="card upload-card">
        <FileUpload file={file} onChange={setFile} onError={setError} disabled={loading} />
        {error ? <div className="alert">{error}</div> : null}
        <button className="primary-button" type="button" onClick={handleAnalyze} disabled={loading || !file}>
          {loading ? <Loader2 className="spin" size={18} /> : null}
          {loading ? 'Analizando CSV...' : 'Analizar CSV'}
        </button>
      </section>

      {response ? (
        <>
          <section className="summary-grid">
            <article className="metric-card">
              <span>Total analizado</span>
              <strong>{response.resumen.total_analizados}</strong>
            </article>
            <article className="metric-card">
              <span>Confianza sentimiento</span>
              <strong>{formatPercent(response.resumen.confianza_promedio_sentimiento)}</strong>
            </article>
            <article className="metric-card">
              <span>Confianza bot</span>
              <strong>{formatPercent(response.resumen.confianza_promedio_bot)}</strong>
            </article>
            <article className="metric-card">
              <span>Errores</span>
              <strong>{response.resumen.errores}</strong>
            </article>
          </section>

          <section className="chart-grid">
            <SentimentChart data={response.resumen.distribucion_sentimiento} />
            <BotChart data={response.resumen.distribucion_bot} />
          </section>

          <section className="card table-card">
            <div className="table-toolbar">
              <div>
                <span className="section-kicker">Resultados</span>
                <h2>Comentarios analizados</h2>
              </div>
              <button className="secondary-button" type="button" onClick={exportResults}>
                <Download size={17} />
                Exportar CSV
              </button>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Comentario</th>
                    <th>Sentimiento</th>
                    <th>Confianza S.</th>
                    <th>Bot</th>
                    <th>Confianza B.</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleRows.map((item, index) => (
                    <tr key={`${item.comentario}-${index}`}>
                      <td>{(page - 1) * PAGE_SIZE + index + 1}</td>
                      <td>{item.comentario}</td>
                      <td>{item.sentimiento.clase}</td>
                      <td>{formatPercent(item.sentimiento.confianza)}</td>
                      <td>{item.bot.clase}</td>
                      <td>{formatPercent(item.bot.confianza)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <button
                className="secondary-button"
                type="button"
                disabled={page === 1}
                onClick={() => setPage((current) => current - 1)}
              >
                Anterior
              </button>
              <span>
                Pagina {page} de {totalPages}
              </span>
              <button
                className="secondary-button"
                type="button"
                disabled={page === totalPages}
                onClick={() => setPage((current) => current + 1)}
              >
                Siguiente
              </button>
            </div>
          </section>
        </>
      ) : null}
    </div>
  )
}

export default BulkAnalysis
