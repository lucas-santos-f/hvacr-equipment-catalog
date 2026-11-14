import { describe, expect, it } from 'vitest'

import { createSnapshotApi } from '../src/api/snapshot.js'
import snapshot from '../src/api/catalog-snapshot.json'
import cases from './fixtures/compare-cases.json'

const api = createSnapshotApi(snapshot)

function unit(model, overrides) {
  return { ...snapshot.items[0], model, ...overrides }
}

describe('snapshot api', () => {
  it('returns the first page of the catalogue sorted by capacity', async () => {
    const page = await api.searchEquipment()
    expect(page.total).toBe(snapshot.items.length)
    expect(page.items).toHaveLength(50)
    const capacities = page.items.map((u) => u.capacity_kw)
    expect(capacities).toEqual([...capacities].sort((a, b) => a - b))
  })

  it('applies every filter together, with the capacity window inclusive', async () => {
    const chiller = snapshot.items.find((u) => u.category === 'chiller')
    const page = await api.searchEquipment({
      category: 'chiller',
      refrigerant: chiller.refrigerant,
      manufacturer: chiller.manufacturer,
      min_capacity: String(chiller.capacity_kw),
      max_capacity: String(chiller.capacity_kw),
    })
    expect(page.items.map((u) => u.model)).toContain(chiller.model)
    for (const u of page.items) {
      expect(u.category).toBe('chiller')
      expect(u.refrigerant).toBe(chiller.refrigerant)
      expect(u.manufacturer).toBe(chiller.manufacturer)
      expect(u.capacity_kw).toBe(chiller.capacity_kw)
    }
  })

  it('treats blank filters as unset, like the query builder does', async () => {
    const page = await api.searchEquipment({
      category: '',
      refrigerant: '',
      manufacturer: '',
      min_capacity: '',
      max_capacity: '',
    })
    expect(page.total).toBe(snapshot.items.length)
  })

  it('pages with limit and offset and still reports the full total', async () => {
    const page = await api.searchEquipment({ limit: 10, offset: 85 })
    expect(page.items).toHaveLength(snapshot.items.length - 85)
    expect(page.items[0]).toEqual(snapshot.items[85])
    expect(page.total).toBe(snapshot.items.length)
  })

  it('rejects a capacity window that is upside down or negative', async () => {
    await expect(api.searchEquipment({ min_capacity: 50, max_capacity: 10 })).rejects.toMatchObject({
      status: 422,
      message: 'min_capacity cannot be greater than max_capacity',
    })
    await expect(api.searchEquipment({ min_capacity: -1 })).rejects.toMatchObject({ status: 422 })
  })

  it('answers 404 for a model that is not in the catalogue', async () => {
    await expect(api.getEquipment('NOPE-1')).rejects.toMatchObject({
      status: 404,
      message: 'unknown model NOPE-1',
    })
    await expect(api.compare(['NOPE-1', snapshot.items[0].model])).rejects.toMatchObject({
      status: 404,
    })
  })

  it('compares 2 to 4 units and nothing else', async () => {
    const models = snapshot.items.slice(0, 5).map((u) => u.model)
    await expect(api.compare(models.slice(0, 1))).rejects.toMatchObject({ status: 422 })
    await expect(api.compare(models)).rejects.toMatchObject({ status: 422 })
  })

  it('gives the same comparison as the backend on every exported case', async () => {
    expect(cases.length).toBeGreaterThan(10)
    for (const { models, expected } of cases) {
      expect(await api.compare(models)).toEqual(expected)
    }
  })

  it('leaves a tied row without a winner', async () => {
    const tied = createSnapshotApi({
      ...snapshot,
      items: [unit('A-1', { price_eur: 1000 }), unit('B-1', { price_eur: 1000, weight_kg: 1 })],
    })
    const { rows } = await tied.compare(['A-1', 'B-1'])
    expect(rows.find((r) => r.field === 'price_eur').best).toBeNull()
    expect(rows.find((r) => r.field === 'weight_kg').best).toBe('B-1')
  })

  it('serves the facets the backend exported', async () => {
    expect(await api.getFacets()).toEqual(snapshot.facets)
  })
})
