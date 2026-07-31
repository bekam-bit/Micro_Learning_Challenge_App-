import api from './axios'

export async function login(username, password){
  const res = await api.post('/auth/token/', { username, password })
  const { access, refresh } = res.data
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
  return res.data
}

export function logout(){
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function refreshToken(){
  const refresh = localStorage.getItem('refresh_token')
  if(!refresh) return null
  const res = await api.post('/auth/token/refresh/', { refresh })
  localStorage.setItem('access_token', res.data.access)
  return res.data
}

export function getAuthHeaders(){
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}
