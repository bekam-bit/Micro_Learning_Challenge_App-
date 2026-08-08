import axios from 'axios'

const DEFAULT_API_BASE_URL = '/api'

// Support direct deployment URLs and local dev proxying through /api.
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.BACKEND_BASE_URL || DEFAULT_API_BASE_URL
const baseURL = rawBaseUrl.replace(/\/+$/, '')
const apiBaseURL = baseURL.startsWith('http') ? `${baseURL}/api` : baseURL

const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 30000, // 30 second timeout
})

const RETRYABLE_STATUS_CODES = new Set([502, 503, 504])
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// Attach access token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status
    const config = error.config

    // Handle 401 Unauthorized - try to refresh token
    if (status === 401 && !config.__retryAuth) {
      config.__retryAuth = true
      
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (refresh) {
          // Try to refresh the token
          const refreshResponse = await axios.post(`${apiBaseURL}/auth/token/refresh/`, { refresh })
          const newAccessToken = refreshResponse.data.access
          
          // Save new access token
          localStorage.setItem('access_token', newAccessToken)
          
          // Retry the original request with new token
          config.headers.Authorization = `Bearer ${newAccessToken}`
          return api.request(config)
        }
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // Don't redirect during page load or for non-essential endpoints
        if (typeof window !== 'undefined' && !config.url?.includes('/auth/')) {
          console.error('Session expired. Please login again.')
          // Only redirect if not already on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login?session_expired=true'
          }
        }
        return Promise.reject(refreshError)
      }
    }

    if (config && RETRYABLE_STATUS_CODES.has(status) && !config.__retryOnce) {
      config.__retryOnce = true
      await wait(1500)
      return api.request(config)
    }

    return Promise.reject(error)
  }
)

export function formatApiError(err, fallback = 'An unexpected error occurred.') {
  if (!err) return fallback
  if (typeof err === 'string') return err

  const status = err.response?.status
  if (RETRYABLE_STATUS_CODES.has(status)) {
    return 'Server is temporarily unavailable (it may be waking up). Please retry in a few seconds.'
  }

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

