// Rules for the compare tray. The backend accepts 2 to 4 models, so the UI has to
// hold the user to the same window before it lets them hit compare.

export const MIN_COMPARE = 2
export const MAX_COMPARE = 4

export function toggle(selection, model) {
  if (selection.includes(model)) {
    return selection.filter((m) => m !== model)
  }
  if (selection.length >= MAX_COMPARE) {
    return selection
  }
  return [...selection, model]
}

export function canCompare(selection) {
  return selection.length >= MIN_COMPARE && selection.length <= MAX_COMPARE
}

export function selectionHint(selection) {
  if (selection.length === 0) return 'Pick at least two units to compare'
  if (selection.length === 1) return 'Pick one more'
  if (selection.length >= MAX_COMPARE) return `Comparing ${MAX_COMPARE}, the maximum`
  return `Comparing ${selection.length}`
}

export function formatPrice(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '-'
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

const LABELS = {
  capacity_kw: 'Capacity (kW)',
  power_input_kw: 'Power input (kW)',
  cop: 'COP',
  sound_pressure_db: 'Sound pressure (dB)',
  weight_kg: 'Weight (kg)',
  price_eur: 'Price',
}

export function fieldLabel(field) {
  return LABELS[field] ?? field
}

export function formatValue(field, value) {
  if (field === 'price_eur') return formatPrice(value)
  if (typeof value !== 'number') return value ?? '-'
  return String(value)
}
