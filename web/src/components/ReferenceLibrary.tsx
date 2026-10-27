import type { LibraryHit } from '../types';
import type { useLibrary } from '../hooks/useLibrary';
import { recordTitle, recordField, sourceNames } from '../presentation';

export default function ReferenceLibrary({ library: l, onInspect, selected, onToggleReference }: { library: ReturnType<typeof useLibrary>; onInspect: (hit: LibraryHit) => void; selected: LibraryHit[]; onToggleReference: (hit: LibraryHit) => void }) {
  return <details className="reference-library" open><summary>Reference library · search the full collection</summary>
    <p>Find musical vocabulary, guidance and complete recipes. All active sources are searchable; V6-targeted core results come first.</p>
    <form className="library-search" onSubmit={event => { event.preventDefault(); l.search(); }}>
      <label htmlFor="reference-query">Search references<input id="reference-query" type="search" value={l.query} maxLength={300} placeholder="Try Mongolian, kawaii, metal, or close vocal" onChange={event => l.setQuery(event.target.value)}/></label>
      <div className="library-filters"><label htmlFor="reference-scope">Reference scope<select id="reference-scope" value={l.scope} onChange={event => l.setScope(event.target.value as 'all' | 'v6_core')}><option value="all">All active references · V6 first</option><option value="v6_core">V6-targeted core only</option></select></label>
        <label htmlFor="reference-kind">Record type<select id="reference-kind" value={l.kind} onChange={event => l.setKind(event.target.value)}><option value="">Any record</option><option value="recipe">Recipes</option><option value="term">Terms</option><option value="phrase">Phrases</option><option value="guidance">Guidance</option></select></label>
        <button type="submit" disabled={l.busy || !l.query.trim()}>{l.busy ? 'Searching…' : 'Search references'}</button>
      </div>
    </form>
    <div aria-live="polite">{l.error && <p className="error" role="alert">{l.error}</p>}{l.notice && <p className="notice" role="status">{l.notice}</p>}{l.changed && <p className="changed">Search inputs changed. Search again to apply them; the results below still belong to the previous search.</p>}</div>
    {!l.page ? <p className="library-empty">Search the collection directly, including vocabulary outside the reviewed concept palette.</p> : <>
      <p className="library-result-count" role="status">{l.page.items.length} {l.page.items.length === 1 ? 'result' : 'results'} shown for “{l.page.query}” · {l.page.scope === 'v6_core' ? 'V6-targeted core' : 'all active references'}{l.page.has_more ? ' · more matches available' : ''}</p>
      {l.page.search_plan?.expanded && <p className="quiet">Reviewed search expansion: {l.page.search_plan.term_groups.map(group => group.join(' / ')).join(' + ')}. Related vocabulary is not evidence of equivalent musical effects.</p>}
      {!l.page.items.length && <p className="library-empty">No matches in this scope. Try fewer words, another spelling{l.page.scope === 'v6_core' ? ', or all active references' : ''}. Only explicitly reviewed query expansions are applied.</p>}
      <div className="library-results">{l.page.items.map(hit => <article className="library-result" key={`${hit.snapshot_id}:${hit.record.id}`}>
        <div className="library-result-meta"><span>{sourceNames[hit.source.id] || hit.source.id}</span><span>{recordField(hit.record)}</span><span>{hit.source.license}</span></div>
        <h3>{recordTitle(hit.record)}</h3>
        <p className={`library-model ${hit.v6_core ? 'core' : ''}`}>{hit.v6_core ? 'V6-targeted core · effects not independently verified' : `Supplementary · ${hit.record.evidence?.model_scope.length ? `source scope: ${hit.record.evidence.model_scope.join(', ')}` : 'model applicability unspecified'}`}</p>
        <p className="library-wording">{'style_prompt' in hit.record ? hit.record.style_prompt : hit.record.meaning}</p>
        <div className="library-result-actions"><button onClick={() => onToggleReference(hit)}>{selected.some(value => value.snapshot_id === hit.snapshot_id && value.record.id === hit.record.id) ? 'Remove from draft' : 'Keep with draft'}</button><button onClick={() => onInspect(hit)}>Inspect reference</button><button disabled={l.exporting} onClick={() => l.exportRecord(hit)}>Export reference JSON</button></div>
      </article>)}</div>
      {l.page.has_more && (l.page.limit < 100 ? <button disabled={l.busy || l.changed} onClick={() => l.search(Math.min(100, l.page!.limit + 20))}>Show more matches</button> : <p className="quiet">First 100 matches shown. Refine the query or record type to narrow the results.</p>)}
    </>}
  </details>;
}
