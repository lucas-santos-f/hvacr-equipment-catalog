import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, api, query } from '../src/api/client.js'

function mockFetch(status, body) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: status < 400,
    status,
    statusText: 'error',
    json: async () => body,
  })
  globalThis.fetch = fetchMock
  return fetchMock
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('query', () => {
  it('drops empty values instead of sending blanks', () => {
    expect(query({ category: 'chiller', refrigerant: '', manufacturer: undefined })).toBe(
      '?category=chiller',
    )
  })

  it('returns an empty string when nothing is set', () => {
    expect(query({ a: null, b: '' })).toBe('')
  })

  it('keeps a zero, which is a real filter value', () => {
    expect(query({ min_capacity: 0 })).toBe('?min_capacity=0')
  })
})

describe('api', () => {
  it('builds the search URL from the filters', async () => {
    const fetchMock = mockFetch(200, { items: [], total: 0 })
    await api.searchEquipment({ category: 'chiller', min_capacity: 50 })
    expect(fetchMock.mock.calls[0][0]).toContain('/equipment?category=chiller&min_capacity=50')
  })

  it('joins models with a comma when comparing', async () => {
    const fetchMock = mockFetch(200, { models: [], rows: [] })
    await api.compare(['TX-CH900', 'NV-CH901'])
    expect(decodeURIComponent(fetchMock.mock.calls[0][0])).toContain(
      'models=TX-CH900,NV-CH901',
    )
  })

  it('escapes a model code with a slash in it', async () => {
    const fetchMock = mockFetch(200, {})
    await api.getEquipment('TX/900')
    expect(fetchMock.mock.calls[0][0]).toContain('TX%2F900')
  })

  it('raises ApiError carrying the status and the backend detail', async () => {
    mockFetch(404, { detail: 'unknown model NOPE-1' })
    await expect(api.getEquipment('NOPE-1')).rejects.toMatchObject({
      status: 404,
      message: 'unknown model NOPE-1',
    })
  })

  it('survives an error body that is not json', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => {
        throw new Error('not json')
      },
    })
    await expect(api.getFacets()).rejects.toBeInstanceOf(ApiError)
  })
})
