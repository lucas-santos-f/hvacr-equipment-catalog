import { describe, expect, it } from 'vitest'

import {
  MAX_COMPARE,
  canCompare,
  fieldLabel,
  formatPrice,
  formatValue,
  selectionHint,
  toggle,
} from '../src/lib/selection.js'

describe('toggle', () => {
  it('adds a model that is not selected', () => {
    expect(toggle([], 'TX-CH900')).toEqual(['TX-CH900'])
  })

  it('removes a model that is already selected', () => {
    expect(toggle(['A', 'B'], 'A')).toEqual(['B'])
  })

  it('refuses a fifth model', () => {
    const full = ['A', 'B', 'C', 'D']
    expect(toggle(full, 'E')).toEqual(full)
  })

  it('still lets you deselect once the tray is full', () => {
    expect(toggle(['A', 'B', 'C', 'D'], 'C')).toEqual(['A', 'B', 'D'])
  })

  it('does not mutate the array it was given', () => {
    const original = ['A']
    toggle(original, 'B')
    expect(original).toEqual(['A'])
  })
})

describe('canCompare', () => {
  it.each([
    [[], false],
    [['A'], false],
    [['A', 'B'], true],
    [['A', 'B', 'C', 'D'], true],
  ])('%j -> %s', (selection, expected) => {
    expect(canCompare(selection)).toBe(expected)
  })
})

describe('selectionHint', () => {
  it('asks for two when nothing is picked', () => {
    expect(selectionHint([])).toMatch(/at least two/)
  })

  it('asks for one more when a single unit is picked', () => {
    expect(selectionHint(['A'])).toBe('Pick one more')
  })

  it('says the tray is full at the maximum', () => {
    expect(selectionHint(['A', 'B', 'C', 'D'])).toContain(String(MAX_COMPARE))
  })
})

describe('formatting', () => {
  it('renders euros without cents', () => {
    expect(formatPrice(62000)).toMatch(/62,000/)
  })

  it('falls back to a dash when the price is missing', () => {
    expect(formatPrice(undefined)).toBe('-')
    expect(formatPrice(Number.NaN)).toBe('-')
  })

  it('labels known fields and passes unknown ones through', () => {
    expect(fieldLabel('cop')).toBe('COP')
    expect(fieldLabel('made_up')).toBe('made_up')
  })

  it('routes price through the currency formatter and leaves others alone', () => {
    expect(formatValue('price_eur', 1000)).toMatch(/1,000/)
    expect(formatValue('capacity_kw', 42)).toBe('42')
    expect(formatValue('refrigerant', 'R32')).toBe('R32')
  })
})
