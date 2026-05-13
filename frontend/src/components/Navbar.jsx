import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Activity, Radar } from 'lucide-react'
import { getHealth } from '../services/api'

function Navbar() {
  const [health, setHealth] = useState(null)
  const [online, setOnline] = useState(false)

  useEffect(() => {
    let mounted = true

    async function checkHealth() {
      try {
        const response = await getHealth()
        if (mounted) {
          setHealth(response)
          setOnline(true)
        }
      } catch {
        if (mounted) {
          setHealth(null)
          setOnline(false)
        }
      }
    }

    checkHealth()
    const intervalId = window.setInterval(checkHealth, 15000)
    return () => {
      mounted = false
      window.clearInterval(intervalId)
    }
  }, [])

  return (
    <header className="navbar">
      <NavLink to="/" className="brand" aria-label="SentinelAI">
        <span className="brand-icon">
          <Radar size={22} />
        </span>
        <span>
          <strong>SentinelAI</strong>
          <small>XLM-RoBERTa Command Center</small>
        </span>
      </NavLink>

      <nav className="nav-links" aria-label="Navegacion principal">
        <NavLink to="/" end>
          Analisis Individual
        </NavLink>
        <NavLink to="/bulk">Analisis Masivo</NavLink>
      </nav>

      <div className={`api-status ${online ? 'online' : 'offline'}`}>
        <span />
        <Activity size={16} />
        <strong>{online ? 'API activa' : 'API offline'}</strong>
        {health?.modo_degradado ? <small>modo degradado</small> : null}
      </div>
    </header>
  )
}

export default Navbar
