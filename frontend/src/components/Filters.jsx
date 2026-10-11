export default function Filters({ facets, filters, onChange, onReset }) {
  function set(key, value) {
    onChange({ ...filters, [key]: value })
  }

  const categories = facets?.categories ?? []
  const refrigerants = facets?.refrigerants ?? []
  const manufacturers = facets?.manufacturers ?? []

  return (
    <section className="filters">
      <label>
        Category
        <select value={filters.category} onChange={(e) => set('category', e.target.value)}>
          <option value="">any</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c.replace('_', ' ')}</option>
          ))}
        </select>
      </label>

      <label>
        Refrigerant
        <select value={filters.refrigerant} onChange={(e) => set('refrigerant', e.target.value)}>
          <option value="">any</option>
          {refrigerants.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </label>

      <label>
        Manufacturer
        <select value={filters.manufacturer} onChange={(e) => set('manufacturer', e.target.value)}>
          <option value="">any</option>
          {manufacturers.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </label>

      <label>
        Min kW
        <input
          type="number"
          min="0"
          value={filters.min_capacity}
          onChange={(e) => set('min_capacity', e.target.value)}
        />
      </label>

      <label>
        Max kW
        <input
          type="number"
          min="0"
          value={filters.max_capacity}
          onChange={(e) => set('max_capacity', e.target.value)}
        />
      </label>

      <button type="button" onClick={onReset}>Reset</button>
    </section>
  )
}
