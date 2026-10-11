// Every call to the backend goes through this file. Components never build a URL
// or touch fetch directly, so the base URL and error handling live in one place.

const BASE = import.meta.env?.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `request failed with ${status}`)
    this.status = status
  }
}

function query(params) {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    search.append(key, value)
  }
  const s = search.toString()
  return s ? `?${s}` : ''
}

async function request(path) {
  const response = await fetch(`${BASE}${path}`)
  if (!response.ok) {
    let detail = ''
    try {
      detail = (await response.json()).detail
    } catch {
      detail = response.statusText
    }
    throw new ApiError(response.status, typeof detail === 'string' ? detail : 'invalid request')
  }
  return response.json()
}

export const api = {
  searchEquipment: (filters = {}) => request(`/equipment${query(filters)}`),
  getEquipment: (model) => request(`/equipment/${encodeURIComponent(model)}`),
  compare: (models) => request(`/equipment/compare${query({ models: models.join(',') })}`),
  getFacets: () => request('/facets'),
}

export { query, BASE }
