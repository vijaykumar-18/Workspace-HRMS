import { createContext, useContext, useEffect, useState } from 'react'
import axiosClient from '../api/axiosClient'
const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem('hrms_user')) } catch { return null } })
  const [loading, setLoading] = useState(false)
  async function login(username, password) {
    const { data } = await axiosClient.post('/auth/login', { username, password })
    localStorage.setItem('hrms_token', data.access_token)
    const me = await axiosClient.get('/auth/me')
    localStorage.setItem('hrms_user', JSON.stringify(me.data)); setUser(me.data); return me.data
  }
  async function register(payload) { return axiosClient.post('/auth/register', payload) }
  function logout() { localStorage.removeItem('hrms_token'); localStorage.removeItem('hrms_user'); setUser(null) }
  useEffect(() => { if (localStorage.getItem('hrms_token') && !user) axiosClient.get('/auth/me').then(r => { setUser(r.data); localStorage.setItem('hrms_user', JSON.stringify(r.data)) }).catch(() => logout()) }, [])
  return <AuthContext.Provider value={{ user, login, register, logout, loading }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
