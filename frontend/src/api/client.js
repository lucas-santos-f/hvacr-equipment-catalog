// Every call to the backend goes through this file. Components never build a URL
// or touch fetch directly, so the base URL and error handling live in one place.

// Render can only inject a bare hostname into a build variable, so accept either form.
function normaliseBase(value) {
  if (!value) return 'http://localhost:8000'
  const trimmed = value.trim().replace(/\/$/, '')
  return /^https?:\/\//.test(trimmed) ? trimmed : `https://${trimmed}`
}

const BASE = normaliseBase(import.meta.env?.VITE_API_URL)

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

const http = {
  searchEquipment: (filters = {}) => request(`/equipment${query(filters)}`),
  getEquipment: (model) => request(`/equipment/${encodeURIComponent(model)}`),
  compare: (models) => request(`/equipment/compare${query({ models: models.join(',') })}`),
  getFacets: () => request('/facets'),
}

// `vite build --mode demo` is the public static demo: no API runs behind it, so the
// same calls are answered from a snapshot of the catalogue. See ./snapshot.js.
export const STATIC_DEMO = import.meta.env.MODE === 'demo'

let snapshotApi
function fromSnapshot(method) {
  return async (...args) => {
    snapshotApi ??= Promise.all([import('./snapshot.js'), import('./catalog-snapshot.json')])
      .then(([{ createSnapshotApi }, data]) => createSnapshotApi(data.default))
    return (await snapshotApi)[method](...args)
  }
}

export const api = STATIC_DEMO
  ? Object.fromEntries(Object.keys(http).map((method) => [method, fromSnapshot(method)]))
  : http

export { query, BASE, normaliseBase }
