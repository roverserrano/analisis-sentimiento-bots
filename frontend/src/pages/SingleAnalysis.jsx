import { useState } from 'react'
import { Loader2, Send } from 'lucide-react'
import ResultCard from '../components/ResultCard'
import { analyzeComment, getApiErrorMessage } from '../services/api'

function SingleAnalysis() {
  const [comment, setComment] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    if (!comment.trim()) {
      setError('Ingresa un comentario antes de analizar.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await analyzeComment(comment)
      setResult(response)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-grid">
      <section className="hero-panel">
        <span className="section-kicker">Analisis individual</span>
        <h1>Detecta polaridad y senales de bot en un comentario.</h1>
        <p>
          SentinelAI envia el texto a dos modelos XLM-RoBERTa: uno clasifica sentimiento y
          otro estima si el comentario fue generado por bot.
        </p>
      </section>

      <section className="card form-card">
        <form onSubmit={handleSubmit}>
          <label htmlFor="comment">Comentario</label>
          <textarea
            id="comment"
            value={comment}
            rows={9}
            maxLength={2000}
            placeholder="Ejemplo: El servicio fue excelente, me atendieron muy rapido."
            onChange={(event) => setComment(event.target.value)}
          />

          {error ? <div className="alert">{error}</div> : null}

          <button className="primary-button" type="submit" disabled={loading || !comment.trim()}>
            {loading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            {loading ? 'Analizando...' : 'Analizar'}
          </button>
        </form>
      </section>

      <ResultCard result={result} />
    </div>
  )
}

export default SingleAnalysis

