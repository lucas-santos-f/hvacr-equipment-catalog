import { fieldLabel, formatValue } from '../lib/selection.js'

export default function ComparisonTable({ comparison }) {
  return (
    <section>
      <h2>Comparison</h2>
      <table>
        <thead>
          <tr>
            <th scope="col">Field</th>
            {comparison.models.map((m) => (
              <th key={m} scope="col">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {comparison.rows.map((row) => (
            <tr key={row.field}>
              <th scope="row">{fieldLabel(row.field)}</th>
              {comparison.models.map((m) => (
                <td key={m} className={row.best === m ? 'best' : undefined}>
                  {formatValue(row.field, row.values[m])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="hint">Highlighted cells are the better figure on that row. Ties are left plain.</p>
    </section>
  )
}
