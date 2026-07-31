import { useState } from 'react'
import api from '../api/axios'

export default function ApiTest() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const testConnection = async () => {
    setLoading(true)
    setResult(null)

    try {
      // Try to hit a simple endpoint
      const response = await api.get('/auth/profile/')
      setResult({
        success: true,
        message: 'Connection successful!',
        data: response.data,
      })
    } catch (err) {
      console.error('Connection test failed:', err)
      setResult({
        success: false,
        message: err.message,
        details: {
          hasResponse: !!err.response,
          status: err.response?.status,
          data: err.response?.data,
          config: {
            baseURL: err.config?.baseURL,
            url: err.config?.url,
            method: err.config?.method,
          },
        },
      })
    } finally {
      setLoading(false)
    }
  }

  const testRegister = async () => {
    setLoading(true)
    setResult(null)

    const testUser = {
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
      password: 'testpass123',
    }

    try {
      const response = await api.post('/auth/register/', testUser)
      setResult({
        success: true,
        message: 'Registration successful!',
        data: response.data,
      })
    } catch (err) {
      console.error('Registration test failed:', err)
      setResult({
        success: false,
        message: err.message,
        details: {
          hasResponse: !!err.response,
          status: err.response?.status,
          data: err.response?.data,
          config: {
            baseURL: err.config?.baseURL,
            url: err.config?.url,
            method: err.config?.method,
          },
        },
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold text-white mb-6">API Connection Test</h1>

      <div className="space-y-4 mb-6">
        <div className="bg-slate-800 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-white mb-2">Configuration</h2>
          <pre className="text-xs text-slate-300 overflow-x-auto">
            {JSON.stringify(
              {
                VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
                expected: 'https://learning-challenge.onrender.com',
              },
              null,
              2
            )}
          </pre>
        </div>

        <button
          onClick={testConnection}
          disabled={loading}
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg disabled:opacity-50"
        >
          {loading ? 'Testing...' : 'Test Connection (GET /auth/profile/)'}
        </button>

        <button
          onClick={testRegister}
          disabled={loading}
          className="w-full py-3 px-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg disabled:opacity-50"
        >
          {loading ? 'Testing...' : 'Test Registration (POST /auth/register/)'}
        </button>
      </div>

      {result && (
        <div
          className={`p-4 rounded-lg ${
            result.success ? 'bg-green-900/50 border border-green-700' : 'bg-red-900/50 border border-red-700'
          }`}
        >
          <h3 className="font-bold text-white mb-2">{result.success ? '✅ Success' : '❌ Failed'}</h3>
          <p className="text-sm text-slate-300 mb-3">{result.message}</p>
          <pre className="text-xs text-slate-300 overflow-x-auto bg-slate-900/50 p-3 rounded">
            {JSON.stringify(result.success ? result.data : result.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
