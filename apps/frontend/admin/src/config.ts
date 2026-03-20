const defaultApiBase = '/api'

export const apiBase = (import.meta.env.VITE_API_BASE_URL || defaultApiBase).replace(/\/$/, '')
