import { createContext, useEffect, useMemo, useState } from 'react'
import api from '../api/axios'
import { login as loginRequest, logout as logoutRequest } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('auth_user')
    return raw ? JSON.parse(raw) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function hydrate() {
      const token = localStorage.getItem('access_token')
      if (!token) {
        if (!cancelled) setLoading(false)
        return
      }

      try {
        const res = await api.get('/auth/profile/')
        if (!cancelled) {
          setUser(res.data)
          localStorage.setItem('auth_user', JSON.stringify(res.data))
        }
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('auth_user')
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    hydrate()

    return () => {
      cancelled = true
    }
  }, [])

  const login = async (username, password) => {
    const data = await loginRequest(username, password)
    setUser(data.user)
    localStorage.setItem('auth_user', JSON.stringify(data.user))
    return data
  }

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token')
    try {
      if (refresh) {
        await logoutRequest(refresh)
      }
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('auth_user')
      setUser(null)
    }
  }

  const value = useMemo(() => ({ user, loading, login, logout, setUser }), [user, loading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthContext }