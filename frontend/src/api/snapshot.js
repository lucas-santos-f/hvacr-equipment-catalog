// Answers the four read calls from a snapshot of the catalogue, for the static demo
// build that has no API behind it. The snapshot is exported by the backend
// (make snapshot), direction of "better" per field included, so the rule itself still
// lives in crud.py. tests/snapshot.test.js holds this file to the backend's output.

import { ApiError } from './client.js'

function capacity(value) {
  if (value === undefined || value === null || value === '') return null
  const n = Number(value)
  if (Number.isNaN(n) || n < 0) throw new ApiError(422, 'invalid request')
  return n
}

function pickBest(values, direction) {
  const numeric = Object.entries(values).filter(([, v]) => typeof v === 'number')
  if (numeric.length < 2) return null
  const figures = numeric.map(([, v]) => v)
  const target = direction === 'max' ? Math.max(...figures) : Math.min(...figures)
  const winners = numeric.filter(([, v]) => v === target)
  // A tie has no winner, same as on the server.
  return winners.length === 1 ? winners[0][0] : null
}

export function createSnapshotApi(snapshot) {
  const items = snapshot.items
  const byModel = new Map(items.map((unit) => [unit.model, unit]))

  function find(model) {
    const unit = byModel.get(model)
    if (!unit) throw new ApiError(404, `unknown model ${model}`)
    return unit
  }

  return {
    async searchEquipment(filters = {}) {
      const min = capacity(filters.min_capacity)
      const max = capacity(filters.max_capacity)
      if (min !== null && max !== null && min > max) {
        throw new ApiError(422, 'min_capacity cannot be greater than max_capacity')
      }
      const limit = Number(filters.limit ?? 50)
      const offset = Number(filters.offset ?? 0)
      const matches = items.filter(
        (u) =>
          (!filters.category || u.category === filters.category) &&
          (!filters.refrigerant || u.refrigerant === filters.refrigerant) &&
          (!filters.manufacturer || u.manufacturer === filters.manufacturer) &&
          (min === null || u.capacity_kw >= min) &&
          (max === null || u.capacity_kw <= max),
      )
      return { items: matches.slice(offset, offset + limit), total: matches.length, limit, offset }
    },

    async getEquipment(model) {
      return find(model)
    },

    async compare(models) {
      const wanted = models.map((m) => m.trim()).filter(Boolean)
      if (wanted.length < 2 || wanted.length > 4) {
        throw new ApiError(422, 'compare between 2 and 4 models')
      }
      const units = wanted.map(find)
      const rows = Object.entries(snapshot.comparison_fields).map(([field, direction]) => {
        const values = Object.fromEntries(units.map((u) => [u.model, u[field] ?? null]))
        return { field, values, best: pickBest(values, direction) }
      })
      return { models: wanted, rows }
    },

    async getFacets() {
      return snapshot.facets
    },
  }
}
