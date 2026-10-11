import { MAX_COMPARE, formatPrice } from '../lib/selection.js'

export default function ResultsTable({ items, total, loading, selection, onToggle }) {
  if (loading) return <p>Loading...</p>
  if (items.length === 0) return <p>Nothing matches those filters.</p>

  const trayFull = selection.length >= MAX_COMPARE

  return (
    <section>
      <p>{items.length} of {total} units</p>
      <table>
        <thead>
          <tr>
            <th scope="col"><span className="visually-hidden">Compare</span></th>
            <th scope="col">Model</th>
            <th scope="col">Manufacturer</th>
            <th scope="col">Category</th>
            <th scope="col">Refrigerant</th>
            <th scope="col">kW</th>
            <th scope="col">COP</th>
            <th scope="col">dB</th>
            <th scope="col">Price</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const picked = selection.includes(item.model)
            return (
              <tr key={item.model} className={picked ? 'picked' : undefined}>
                <td>
                  <input
                    type="checkbox"
                    checked={picked}
                    disabled={!picked && trayFull}
                    onChange={() => onToggle(item.model)}
                    aria-label={`Compare ${item.model}`}
                  />
                </td>
                <td>{item.model}</td>
                <td>{item.manufacturer}</td>
                <td>{item.category.replace('_', ' ')}</td>
                <td>{item.refrigerant}</td>
                <td>{item.capacity_kw}</td>
                <td>{item.cop}</td>
                <td>{item.sound_pressure_db || '-'}</td>
                <td>{formatPrice(item.price_eur)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </section>
  )
}
