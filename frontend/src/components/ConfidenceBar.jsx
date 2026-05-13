function ConfidenceBar({ value, color = 'var(--cyan)' }) {
  const percent = Math.round((value || 0) * 100)

  return (
    <div className="confidence">
      <div className="confidence-track" aria-label={`Confianza ${percent}%`}>
        <span style={{ width: `${percent}%`, background: color }} />
      </div>
      <strong>{percent}%</strong>
    </div>
  )
}

export default ConfidenceBar

