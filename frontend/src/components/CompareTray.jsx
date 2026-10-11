import { selectionHint } from '../lib/selection.js'

export default function CompareTray({ selection, enabled, onCompare, onClear }) {
  return (
    <section className="tray">
      <span>{selection.join(', ') || 'No units picked'}</span>
      <span className="hint">{selectionHint(selection)}</span>
      <button type="button" disabled={!enabled} onClick={onCompare}>Compare</button>
      <button type="button" disabled={selection.length === 0} onClick={onClear}>Clear</button>
    </section>
  )
}
