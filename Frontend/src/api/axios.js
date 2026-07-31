import axios from 'axios'

// HARDCODED URL - If this doesn't work, nothing will!
const BACKEND_URL = 'https://learning-challenge.onrender.com'

// Support both VITE_API_BASE_URL (local dev) and BACKEND_BASE_URL (Render)
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.BACKEND_BASE_URL || BACKEND_URL
const baseURL = rawBaseUrl.replace(/\/+$/, '')

console.log('═══════════════════════════════════════════')
console.log('🔧 API Configuration:', {
  HARDCODED_URL: BACKEND_URL,
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  BACKEND_BASE_URL: import.meta.env.BACKEND_BASE_URL,
  rawBaseUrl,
  baseURL,
  finalApiUrl: `${baseURL}/api`,
  mode: import.meta.env.MODE,
})
console.log('═══════════════════════════════════════════')

if (!rawBaseUrl.includes('learning-challenge.onrender.com')) {
  console.error('❌ ERROR: Using wrong backend URL!')
  console.error('Expected: https://learning-challenge.onrender.com')
  console.error('Got:', rawBaseUrl)
  console.error('Please restart your dev server: Ctrl+C then npm run dev')
  alert('⚠️ WRONG BACKEND URL! Check console (F12). You need to restart dev server!')
}

const api = axios.create({
  baseURL: `${baseURL}/api`,
  timeout: 30000, // 30 second timeout
})

// Attach access token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  
  console.log('📤 Making request to:', config.baseURL + config.url)
  return config
})

// Add response interceptor for better error logging
api.interceptors.response.use(
  (response) => {
    console.log('✅ Request successful:', response.config.url, response.status)
    return response
  },
  (error) => {
    console.error('❌ Request failed:', {
      url: error.config?.url,
      method: error.config?.method,
      baseURL: error.config?.baseURL,
      fullURL: error.config?.baseURL + error.config?.url,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data,
    })
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

