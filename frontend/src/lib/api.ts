import axios from 'axios'

/**
 * Axios instance with default configuration
 */
const getBaseURL = () => {
  // Check if we have environment variable
  if (import.meta.env.VITE_API_URL) {
    console.log('[API] Using VITE_API_URL:', import.meta.env.VITE_API_URL)
    return import.meta.env.VITE_API_URL
  }
  
  // Development: use localhost:8000
  if (import.meta.env.DEV) {
    console.log('[API] Using DEV mode: http://localhost:8000/api')
    return 'http://localhost:8000/api'
  }
  
  // Production: use relative path (nginx will proxy)
  console.log('[API] Using PROD mode: /api')
  return '/api'
}

const baseURL = getBaseURL()
console.log('[API] Final baseURL:', baseURL)

export const api = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request interceptor
 */
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

