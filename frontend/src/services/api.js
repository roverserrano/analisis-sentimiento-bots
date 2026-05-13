import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 120000,
})

export async function getHealth() {
  const response = await api.get('/api/health')
  return response.data
}

export async function analyzeComment(comentario) {
  const response = await api.post('/api/analyze', { comentario })
  return response.data
}

export async function analyzeBulk(comentarios) {
  const response = await api.post('/api/analyze/bulk', { comentarios })
  return response.data
}

export async function analyzeCsv(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/api/analyze/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export function getApiErrorMessage(error) {
  const detail = error?.response?.data?.detail

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(' ')
  }

  if (typeof detail === 'string') {
    return detail
  }

  if (error?.code === 'ECONNABORTED') {
    return 'La solicitud tardo demasiado. Intenta con menos comentarios.'
  }

  return 'No se pudo conectar con la API. Verifica que FastAPI este en ejecucion.'
}

