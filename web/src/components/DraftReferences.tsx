import type { LibraryHit } from '../types';
import { recordTitle, sourceNames } from '../presentation';

type Props = { references: LibraryHit[]; inactive: LibraryHit[]; onRemove: (hit: LibraryHit) => void; onInspect: (hit: LibraryHit) => void };

export default function DraftReferences({ references, inactive, onRemove, onInspect }: Props) {
  if (!references.length) return null;
  return <section className="draft-references" aria-label="References kept with draft">
    <h2>References kept with this draft <span>{references.length} / 50</span></h2>
    <p>These choices stay across searches and are saved with the draft. Source wording, model status and licenses travel with them.</p>
    {references.map(hit => <article key={`${hit.snapshot_id}:${hit.record.id}`}>
      <h3>{recordTitle(hit.record)}</h3>
      <p className="quiet">{sourceNames[hit.source.id] || hit.source.id} · {hit.source.license} · revision {hit.source.revision.slice(0, 12)} · {hit.v6_core ? 'V6-targeted core' : 'Supplementary reference'}</p>
      {inactive.some(value => value.snapshot_id === hit.snapshot_id && value.record.id === hit.record.id) && <p className="changed">Historical source version. The saved reference is retained unchanged. Source activity is checked when the draft is opened.</p>}
      <div className="library-result-actions"><button onClick={() => onInspect(hit)}>Inspect kept reference</button><button onClick={() => onRemove(hit)}>Remove kept reference</button></div>
    </article>)}
  </section>;
}
