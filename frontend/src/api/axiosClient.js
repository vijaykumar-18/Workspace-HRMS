import axios from 'axios'
const axiosClient = axios.create({ baseURL: 'http://127.0.0.1:8000/api/v1' })
axiosClient.interceptors.request.use(config => {
  const token = localStorage.getItem('hrms_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
axiosClient.interceptors.response.use(response => response, error => {
  if (error.response?.status === 401) {
    localStorage.removeItem('hrms_token')
    localStorage.removeItem('hrms_user')
    if (window.location.pathname !== '/login') window.location.href = '/login'
  }
  return Promise.reject(error)
})
export default axiosClient
