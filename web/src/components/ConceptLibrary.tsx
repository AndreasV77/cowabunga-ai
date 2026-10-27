import type { Concept, Meta } from '../types';

type Props = {
  concepts: Concept[];
  filtered: Concept[];
  meta: Meta | null;
  query: string;
  selected: string[];
  onQueryChange: (value: string) => void;
  onToggleConcept: (id: string) => void;
  onClear: () => void;
};

export default function ConceptLibrary({ concepts, filtered, meta, query, selected, onQueryChange, onToggleConcept, onClear }: Props) {
  return (
      <aside className="library" aria-label="Musical concepts">
        <div className="library-intro"><h2>What should the music do?</h2><p>Choose musical jobs. Explore the wording behind them.</p></div>
        <label className="search-label" htmlFor="concept-search">Find a concept</label>
        <input id="concept-search" type="search" placeholder="Try “intimate singer”" value={query} onChange={e => onQueryChange(e.target.value)}/>
        <div className="library-count">{meta ? `${concepts.length} reviewed concepts` : 'Loading your references…'}{selected.length > 0 && <button className="subtle" onClick={() => onClear()}>Clear selection</button>}</div>
        <nav className="concept-list" aria-label="Concept selection">
          {filtered.map(concept => <button key={concept.id} className={`concept-button ${selected.includes(concept.id) ? 'chosen' : ''}`} aria-pressed={selected.includes(concept.id)} onClick={() => onToggleConcept(concept.id)}>
            <span className="concept-symbol" aria-hidden="true">{selected.includes(concept.id) ? '✓' : '+'}</span>
            <span><strong>{concept.label}</strong><small>{concept.description}</small></span>
          </button>)}
          {meta && !filtered.length && <p className="empty-search">No matching concept. Try “voice”, “chorus” or “bass”.</p>}
        </nav>
        <div className="library-foot"><strong>V6 comes first</strong><p>{meta ? `${meta.core.entries} reference entries and ${meta.core.recipes} recipes in the V6 core.` : 'Source-linked wording from the reviewed V6 core.'}</p><small>Version {meta?.version || '…'}</small></div>
      </aside>
  );
}
