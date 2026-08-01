import axios from 'axios'

const DEFAULT_BACKEND_URL = 'https://learning-challenge.onrender.com'
const DEFAULT_API_BASE_URL = '/api'

// Support direct deployment URLs and local dev proxying through /api.
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.BACKEND_BASE_URL || DEFAULT_API_BASE_URL
const baseURL = rawBaseUrl.replace(/\/+$/, '')
const apiBaseURL = baseURL.startsWith('http') ? `${baseURL}/api` : baseURL

const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 30000, // 30 second timeout
})

// Attach access token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error)
  }
)

export function formatApiError(err, fallback = 'An unexpected error occurred.') {
  if (!err) return fallback
  if (typeof err === 'string') return err

  const data = err.response?.data
  if (!data) {
    if (err.message === 'Network Error' || !err.response) {
      return 'Network error: Cannot connect to the server. Please check your internet connection.'
    }
    return err.message || fallback
  }

  if (typeof data === 'string') return data
  if (data.detail && typeof data.detail === 'string') return data.detail

  if (typeof data === 'object') {
    const messages = []
    for (const [key, value] of Object.entries(data)) {
      const fieldName = key.replace(/_/g, ' ')
      if (Array.isArray(value)) {
        messages.push(`${fieldName}: ${value.join(' ')}`)
      } else if (typeof value === 'string') {
        messages.push(`${fieldName}: ${value}`)
      } else if (typeof value === 'object' && value !== null) {
        messages.push(`${fieldName}: ${JSON.stringify(value)}`)
      }
    }
    if (messages.length > 0) return messages.join('\n')
  }

  return fallback
}

export default api

