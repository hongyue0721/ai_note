const defaultApiBase = 'http://146.190.84.189:8000'

export const apiBase = (import.meta.env.VITE_API_BASE_URL || defaultApiBase).replace(/\/$/, '')
