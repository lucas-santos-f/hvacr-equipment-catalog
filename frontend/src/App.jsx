import { useEffect, useState } from 'react'

import { api } from './api/client.js'
import Filters from './components/Filters.jsx'
import ResultsTable from './components/ResultsTable.jsx'
import CompareTray from './components/CompareTray.jsx'
import ComparisonTable from './components/ComparisonTable.jsx'
import { canCompare, toggle } from './lib/selection.js'

const EMPTY_FILTERS = {
  category: '',
  refrigerant: '',
  manufacturer: '',
  min_capacity: '',
  max_capacity: '',
}

export default function App() {
  const [facets, setFacets] = useState(null)
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [page, setPage] = useState({ items: [], total: 0 })
  const [selection, setSelection] = useState([])
  const [comparison, setComparison] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getFacets().then(setFacets).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    setLoading(true)
    api
      .searchEquipment(filters)
      .then((data) => {
        setPage(data)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [filters])

  async function runComparison() {
    try {
      setComparison(await api.compare(selection))
      setError(null)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <main>
      <header>
        <h1>HVAC-R equipment catalogue</h1>
        <p>Filter by duty and refrigerant, then put up to four units side by side.</p>
      </header>

      {error && <p role="alert" className="error">{error}</p>}

      <Filters
        facets={facets}
        filters={filters}
        onChange={setFilters}
        onReset={() => setFilters(EMPTY_FILTERS)}
      />

      <ResultsTable
        items={page.items}
        total={page.total}
        loading={loading}
        selection={selection}
        onToggle={(model) => setSelection((s) => toggle(s, model))}
      />

      <CompareTray
        selection={selection}
        enabled={canCompare(selection)}
        onCompare={runComparison}
        onClear={() => {
          setSelection([])
          setComparison(null)
        }}
      />

      {comparison && <ComparisonTable comparison={comparison} />}
    </main>
  )
}
