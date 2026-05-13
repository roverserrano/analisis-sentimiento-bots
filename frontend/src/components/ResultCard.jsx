import BotChart from '../charts/BotChart'
import SentimentChart from '../charts/SentimentChart'
import ConfidenceBar from './ConfidenceBar'

const SENTIMENT_COLORS = {
  Bueno: 'var(--good)',
  Regular: 'var(--regular)',
  Malo: 'var(--bad)',
}

function ResultCard({ result }) {
  if (!result) {
    return (
      <section className="card result-card empty-state">
        <span className="section-kicker">Resultado</span>
        <h2>Esperando comentario</h2>
        <p>Ingresa un texto y ejecuta el analisis para ver las predicciones.</p>
      </section>
    )
  }

  const sentimentColor = SENTIMENT_COLORS[result.sentimiento.clase] || 'var(--cyan)'
  const botColor = result.bot.clase === 'Bot' ? 'var(--bot)' : 'var(--good)'

  return (
    <section className="card result-card">
      <span className="section-kicker">Resultado individual</span>
      <blockquote>{result.comentario}</blockquote>

      <div className="prediction-grid">
        <article className="prediction-box">
          <div className="prediction-title">
            <span>Sentimiento</span>
            <strong className="badge" style={{ '--badge-color': sentimentColor }}>
              {result.sentimiento.clase}
            </strong>
          </div>
          <ConfidenceBar value={result.sentimiento.confianza} color={sentimentColor} />
        </article>

        <article className="prediction-box">
          <div className="prediction-title">
            <span>Bot</span>
            <strong className="badge" style={{ '--badge-color': botColor }}>
              {result.bot.clase}
            </strong>
          </div>
          <ConfidenceBar value={result.bot.confianza} color={botColor} />
        </article>
      </div>

      <div className="mini-chart-grid">
        <SentimentChart data={result.sentimiento.probabilidades} title="Probabilidades" />
        <BotChart data={result.bot.probabilidades} title="Bot vs No bot" />
      </div>
    </section>
  )
}

export default ResultCard

